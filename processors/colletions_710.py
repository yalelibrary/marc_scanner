from base_processor import BaseProcessor
from marc.marc_helpers import record_id, record_type


#
#  Look for 710 with $5
#   create a tsv file containing bib `id<tab>$5<tab>710` for records that have $5 with is not 'CtY-BT' (non_brbl_710_5.tsv)
#   create a tsv file containing bib `id<tab>$5<tab>710` for records that have $5 'CtY-BT' (brbl_710_5.tsv)
#   count variations of 710$5 `710$5 Values`
#
class Collections710(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        if record_type(record) == 'bibliographic':
            for field710 in record.get_fields('710'):
                if field710:
                    subfield_5s = field710.get_subfields('5')
                    for subfield in subfield_5s:
                        self.reporter.add_count_value('710$5 Values', subfield)
                        if subfield != 'CtY-BR':
                            self.reporter.write_line(
                                'non_brbl_710_5.tsv',
                                [record_id(record), subfield, field710],
                            )
                        else:
                            self.reporter.write_line(
                                'brbl_710_5.tsv',
                                [record_id(record), subfield, field710],
                            )
