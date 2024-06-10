from base_processor import BaseProcessor
from marc.marc_helpers import record_id, record_type
import logging


#
#  Count 9xx field tags, report all that are available,
#    write available 9xx fields to `available_9xx.txt`
#
class Available9xx(BaseProcessor):

    def __init__(self, reporter):
        self.reporter = reporter

    def marc_record(self, record):
        if record_type(record) == 'bibliographic':
            for field9xx in [f for f in record.get_fields() if f.tag.startswith('9')]:
                if field9xx:
                    self.reporter.add_count_value('9xx counts', field9xx.tag)

    def scanning_complete(self):
        report_logger = logging.getLogger('report')
        counts9xx = self.reporter.get_count_value('9xx counts')
        report_logger.info('Available 9xx Fields')
        for x in range(900, 999):
            if not f'{x}' in counts9xx:
                report_logger.info(f'   {x}')
                self.reporter.write_line('available_9xx.txt', x)
