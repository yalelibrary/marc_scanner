class BaseProcessor:
    def __init__(self):
        self.name = 'BaseProcessor'

    def marc_record(self, record):
        pass

    def marc_record_group(self, records):
        pass

    def scanning_complete(self):
        pass
