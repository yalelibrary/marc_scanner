import multiprocessing
from os.path import exists
from pathlib import Path
from sys import stderr
from base_processor import BaseProcessor
from pymarc import JSONWriter, MARCWriter, XMLWriter
from pkgutil import iter_modules
from importlib import import_module
from inspect import isclass
import argparse
import logging
import os, signal
import time
import glob
import traceback
import concurrent.futures, threading
from marc.marc_helpers import is_holding, record_id
from record_generator import PymarcRecordGenerator
from reporter import Reporter

logger = logging.getLogger(__name__)

def configure_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

#
#  Scans marc files and passes records to Processors
#
class Scanner:
    def __init__(self):
        self.cancel = False
        signal.signal(signal.SIGINT, self.sigint_handler)

    def __enter__(self):
        self.reporter = Reporter()
        self.reporter.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.reporter.close()
        self.reporter.print_report()
        for processor in self.processor_list:
            processor.scanning_complete()

    def load_processors(self, processor_names, base_class):
        root = os.path.dirname(__file__)
        processor_directory = os.path.join(root, 'processors')
        processor_directories = [os.path.relpath(x[0], root) for x in os.walk(processor_directory) if not os.path.basename(x[0]).startswith('__')]
        extractors = []
        for a, module_name, b in iter_modules(processor_directories):
            prefix = os.path.relpath(a.path, root).replace(os.sep, '.')
            module = import_module(f'{prefix}.{module_name}')
            print(module)
            for attribute_name in [attribute_name for attribute_name in dir(module) if attribute_name in processor_names]:
                attribute = getattr(module, attribute_name)
                if (
                    isclass(attribute)
                    and issubclass(attribute, base_class)
                    and attribute != base_class
                ):
                    extractors.append(attribute(self.reporter))
        return extractors

    def parse_file(self, file):
        logger.info(f'Parsing {file}')
        with PymarcRecordGenerator(file) as reader:
            for record in reader.records():
                if self.cancel:
                    break
                try:
                    for processor in self.processor_list:
                        processor.marc_record(record)
                except Exception as e:
                    logger.error(f'Error, in file read {file}: {e}')
                    traceback.print_exception(e)

    def parse_file_interleave(self, file):
        logger.info(f'Parsing {file} (interleave)')
        with PymarcRecordGenerator(file) as reader:
            record_group = []
            for record in reader.records():
                if self.cancel:
                    break
                try:
                    for processor in self.processor_list:
                        processor.marc_record(record)
                    if not is_holding(record):
                        if record_group:
                            for processor in self.processor_list:
                                processor.marc_record_group(record_group)
                            record_group = []
                    record_group.append(record)
                    if len(record_group) > 1000:
                        logger.error(f'Record group too large for interleave, clearning for {record_id(record_group[0])}')
                        record_group = [record_group[0]]
                except Exception as e:
                    logger.error(f'Error, processing record in file {file}: {e}, Exiting early')
                    traceback.format_exception(e)
                    break

    def sigint_handler(self, signum, frame):
        self.cancel = True

    def scan_directory(self, files, processors, interleave, max_workers, report_filename):
        start_time = time.time()
        self.processor_list = self.load_processors(processors, BaseProcessor)
        if not self.processor_list:
            logger.error('No processors were found, exiting without scanning')
            raise('No processors were found, exiting without scanning')
        processor_class_names = [processor.__class__.__name__ for processor in self.processor_list]
        missing_processors = [processor for processor in processors if not processor in processor_class_names]
        if missing_processors:
            logger.error(f'Processors not found {missing_processors}, exiting without scanning')
            raise(f'Processors not found {missing_processors}, exiting without scanning')
        self.reporter.set_filename(report_filename)
        logger.info(f'Scanning {files} using {max_workers} max workers')
        parse_func = self.parse_file_interleave if interleave else self.parse_file
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = []
            for file in glob.glob(files):
                results.append(executor.submit(parse_func, file))
            for _ in concurrent.futures.as_completed(results):
                pass
            logger.info(f'done parsing in {(time.time() - start_time)} seconds')
            if self.cancel:
                logger.info(f'Execution was cancelled\n')

def main():
    configure_logging()
    parser = argparse.ArgumentParser(description='Parse MARC Records and generate statistics and reports')
    parser.add_argument('-p', '--processor', required=True, help='processor(s) (comma separated list)')
    parser.add_argument('-n', '--max-workers', type=int, help='maximum number of workers', default = multiprocessing.cpu_count())
    parser.add_argument('-i', '--interleave', help='interleave bibs followed by holdings (files must be interleaved)', action='store_true')
    parser.add_argument('files', help='MARC file(s) to process using file globbing (reads binary MARC, MARC-XML, and MARC-JSON)')
    options = parser.parse_args()
    report_filename = f'{Path(__file__).stem}-{'-'.join(options.processor.split(','))}.log'
    try:
        os.remove(report_filename)
    except FileNotFoundError:
        pass
    with Scanner() as scanner:
        scanner.scan_directory(options.files, options.processor.split(','), options.interleave, options.max_workers, report_filename)

if __name__ == '__main__':
    main()
