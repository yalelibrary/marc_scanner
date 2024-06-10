def is_holding(record):
    return record.leader[6] in 'uvxy'

def is_authority(record):
    return record.leader[6] in 'z'

def record_type(record):
    if record.leader[6] in 'z':
        return 'authority'
    if record.leader[6] in 'uvxy':
        return 'holding'
    if record.leader[6] in 'w':
        return 'classification'
    if record.leader[6] in 'q':
        return 'community'
    return 'bibliographic'

def record_id(record):
    return record['001'].value()

def extract_values(record, field_tag, subfield_tags):
    values = []
    for field in record.get_fields(field_tag):
        values += field.get_subfields(*subfield_tags)
    return values