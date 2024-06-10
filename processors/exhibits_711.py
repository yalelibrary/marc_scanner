import re
from base_processor import BaseProcessor
from marc.marc_helpers import record_id, record_type


#
#  Look for 711 with $i containing 'Exhibit'
#   write all matching records to `exhibits.mrc`
#   create a tsv file containing bib `id<tab>711` for matching records
#   count number of bibs with 711, non of which have Exibit in $i: `711 without Exhibit in $i`
#   count number 711, which have Exibit in $i: `711 with $i Exhibit`
#   count number of each $0 prefix variation in matching 711: `'711$0 prefix'`
#   count number of each $5 variation in matching 711: `711$5`#
#
class Exhibits711(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        if record_type(record) == 'bibliographic':
            for field711 in record.get_fields('711'):
                if field711:
                    exhibit_found = False
                    subfield_is = field711.get_subfields('i')
                    for subfield_i in subfield_is:
                        if 'Exhibit' in subfield_i:
                            self.reporter.write_line(
                                'exhibits.tsv', [record_id(record), field711]
                            )
                            self.reporter.add_count('711 with $i Exhibit')
                            subfield0s = field711.get_subfields('0')
                            if subfield0s:
                                for subfield0 in subfield0s:
                                    self.reporter.add_count_value(
                                        '711$0 prefix', re.sub('\\d', '', subfield0)
                                    )

                            subfield5s = field711.get_subfields('5')
                            if subfield5s:
                                for subfield5 in subfield5s:
                                    self.reporter.add_count_value('711$5', subfield5)

                            exhibit_found = True
                        else:
                            self.reporter.add_count('711 with $i, but without Exhibit')
                    if exhibit_found:
                        self.reporter.write_record('exhibits.mrc', record)
                    else:
                        self.reporter.add_count('711 without Exhibit in $i')
