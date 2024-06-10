from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from pymarc import XmlHandler, MARCReader, JSONReader
from queue import Queue
from threading import Thread
import tarfile
import sys


#
#  Creates a record generator from a marc file in
#     binary MARC, MARC-XML, or MARC-JSON format
#
class PymarcRecordGenerator(XmlHandler):
    def __init__(self, file_name, on_error=None, timeout=1000):
        self.on_error = on_error
        self.call_back = None
        self.q = Queue()
        self.job_done = object()
        self.timeout = timeout
        self._record = None
        self._field = None
        self._subfield_code = None
        self._text = []
        self._strict = False
        self.normalize_form = None
        self.file_name = file_name
        self.xml_source = False

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.read_fh = self.fh = open(self.file_name, 'rb')
        self.xml_source = False
        if self.file_name.endswith('xml') or self.file_name.endswith('gz'):
            self.xml_source = True
            if self.file_name.endswith('gz'):
                tar = tarfile.open(fileobj=self.fh, mode='r:gz')
                for member in tar.getmembers():
                    f = tar.extractfile(member)
                    if f is not None:
                        self.read_fh = f

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()

    def close(self):
        self.fh.close()

    def process_record(self, record):
        self.q.put(record)
        self.q.put('dummy', True, self.timeout)
        self.q.join()

    def parse_handler(self):
        parser = make_parser()
        parser.setContentHandler(self)
        parser.setFeature(feature_namespaces, 1)
        try:
            parser.parse(self.read_fh)
        except Exception as e:
            self.q.put(e)
            self.q.put('dummy', True, self.timeout)
        finally:
            self.q.put(self.job_done)

    def records(self):
        if self.xml_source:
            parser = make_parser()
            parser.setContentHandler(self)
            parser.setFeature(feature_namespaces, 1)
            Thread(target=self.parse_handler, daemon=True).start()
            while True:
                next_item = self.q.get(True, self.timeout)
                self.q.task_done()
                if next_item is self.job_done:
                    break
                if isinstance(next_item, Exception):
                    if self.on_error:
                        self.on_error(next_item)
                        break
                    else:
                        sys.stderr.write(f'{next_item}\n')
                else:
                    yield next_item
                self.q.get()
                self.q.task_done()
        else:
            if self.file_name.endswith('json'):
                marc_reader = JSONReader(self.read_fh)
            else:
                marc_reader = MARCReader(self.read_fh, utf8_handling='ignore')
            for record in marc_reader:
                if record:
                    yield record
                else:
                    if self.on_error:
                        self.on_error(marc_reader.current_exception)
                    else:
                        sys.stderr.write(
                            f'Chunk was ignored because the following exception raised: {marc_reader.current_exception}\n'
                        )
