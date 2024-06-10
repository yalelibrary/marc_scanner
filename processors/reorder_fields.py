from base_processor import BaseProcessor
from marc.marc_helpers import record_type


#
#  Reorder fields based on first digit in field tag
#
class ReorderFields(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        type = record_type(record)
        try:
            new_fields = sorted(record.fields, key=lambda field: int(field.tag[0]))
            if record.fields != new_fields:
                self.reporter.add_count(f'unsorted fields in {type} records')
                self.reporter.write_record(f'pre_sorted_field-{type}.mrc', record)
                self.reporter.write_record('sample_records.mrc', record)
                record.fields = new_fields
                self.reporter.write_record(f'sorted_field-{type}.mrc', record)
        except ValueError:
            self.reporter.write_record(f'invalid-tags-{type}.mrc', record)
