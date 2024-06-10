from base_processor import BaseProcessor
from marc.marc_helpers import record_id


#
#  Example Interleave processor
#
class InterleaveProcessor(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record_group(self, records):
        print(f'Bib {record_id(records[0])}')
        holdings = [r for r in records[1:]]
        for record in holdings:
            print(f'   Holding {record_id(record)}')
