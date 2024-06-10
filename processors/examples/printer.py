from base_processor import BaseProcessor


#
#  Simple processor that prints all records
#
class Printer(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        print(record)
