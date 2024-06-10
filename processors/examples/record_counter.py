from base_processor import BaseProcessor
from marc.marc_helpers import record_type


#
#  Count all records by type
#
class RecordCounter(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        self.reporter.add_count_value('Record Type', record_type(record))
