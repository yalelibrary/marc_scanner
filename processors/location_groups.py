from base_processor import BaseProcessor
from marc.marc_helpers import extract_values, is_holding, record_id, record_type


#
#  Find bibs with more than 5 distinct locations
#
class LocationGroups(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record_group(self, records):
        locations = []
        holdings = [record for record in records if is_holding(record)]
        for holding in holdings:
            locations.append(' '.join(extract_values(holding, '852', ['b', 'c'])))
            self.reporter.add_count('holdings')
        if 'withdrawn' in locations:
            locations.remove('withdrawn')
        if locations:
            locations = list(set(locations))  # dedup
            locations.sort()  # sort
            if len(locations) > 5:
                self.reporter.add_count_value(
                    'Locations Groups > 5', ', '.join(locations)
                )
                self.reporter.write_line(
                    'bibs_with_more_than_5_locations.tsv',
                    [record_id(records[0]), locations],
                )
                for record in records:
                    self.reporter.write_record('location.mrc', record)