from base_processor import BaseProcessor
from marc.marc_helpers import record_id, record_type


#
#  Count and export MMS IDs for records with Yale in 502
#  e.g. `python marc_scanner.py -p Yale502 -n 50 '/Users/netid/Extracts/Alma/*.mrc'`
#
class Yale502(BaseProcessor):
    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        if record_type(record) == 'bibliographic':
            self.reporter.add_count('Bib count')
            yale502s = [f for f in record.get_fields('502') if 'yale' in f'{f}']
            if yale502s:
                self.reporter.add_count('Yale 502 count')
                self.reporter.write_line('yale_502.txt', [record_id(record), f'{yale502s[0]}'])
                self.reporter.write_record('yale_502.mrc', record)
