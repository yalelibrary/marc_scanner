from base_processor import BaseProcessor


#
#  Write all records to three files in .mrc, .xml, and .json formats
#
class AsMarc(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        self.reporter.write_record('records.mrc', record)
        self.reporter.write_record('records.xml', record)
        self.reporter.write_record('records.json', record)
