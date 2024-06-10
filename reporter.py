from pymarc import JSONWriter, MARCWriter, XMLWriter
import logging
import threading

#
#  Reporter to count values and write to files
#    - handles file handles and prints report
#
report_logger = logging.getLogger('report')
logger = logging.getLogger(__file__)


def configure_report_logging(filename):
    logger = logging.getLogger('report')
    logger.setLevel('INFO')
    fh_info = logging.FileHandler(filename)
    logger.addHandler(fh_info)


def create_writer(filename):
    if filename.endswith('xml'):
        return XMLWriter(open(filename, 'wb'))
    if filename.endswith('json'):
        return JSONWriter(open(filename, 'w'))
    return MARCWriter(open(filename, 'wb'))


class Reporter:
    def __init__(self):
        self.write_lock = threading.Lock()
        self.count_lock = threading.Lock()
        self.count_value_lock = threading.Lock()
        self.marc_write_lock = threading.Lock()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()

    def open(self):
        self.counts = {}
        self.count_value = {}
        self.files = {}
        self.marc_files = {}

    def close(self):
        for name in self.files.keys():
            logger.info(f'Closing file {name}')
            self.files[name].close()
        for name in self.marc_files.keys():
            logger.info(f'Closing marc writer {name}')
            self.marc_files[name].close()

    def set_filename(self, filename):
        configure_report_logging(filename)

    def print_report(self):
        if self.counts:
            report_logger.info(f'**************\nCounts\n**************')
            for name in self.counts:
                report_logger.info(f'{name}: {self.counts[name]}')
        if self.count_value:
            for name in self.count_value:
                report_logger.info(f'{name}:')
                for item in sorted(
                    self.count_value[name].items(), key=lambda item: (-item[1], item[0])
                ):
                    report_logger.info(f'\t{item[0]}: {item[1]}')

    def add_count(self, name, count=1):
        with self.count_lock:
            self.counts[name] = self.counts.get(name, 0) + count

    def get_count(self, name):
        return self.counts[name]

    def add_count_value(self, name, value, count=1):
        with self.count_value_lock:
            self.count_value[name] = self.count_value.get(name, {})
            self.count_value[name][value] = self.count_value[name].get(value, 0) + count

    def get_count_value(self, name):
        return self.count_value[name]

    def write_line(self, filename, line):
        if isinstance(line, list):
            line = '\t'.join([f'{col}' for col in line])
        with self.write_lock:
            if not filename in self.files:
                self.files[filename] = open(filename, 'w')
            self.files[filename].write(f'{line}\n')

    def write_record(self, filename, record):
        with self.marc_write_lock:
            if not filename in self.marc_files:
                self.marc_files[filename] = create_writer(filename)
            self.marc_files[filename].write(record)
