from datetime import datetime

from pyexcel.exceptions import FileTypeNotSupported

from soprano.models import Layout, SpotData, Sample

ACQUIRE_TIME_I = 9


def normalize_sheet_file(upload_file):
    try:
        return upload_file.get_sheet()
    except (FileTypeNotSupported, Exception):
        return None


def parse_acquire_time(record, acquire_time_i=ACQUIRE_TIME_I):
    """
    Modifies the record in place to convert the string 'acquire time' field to
    a Python DateTime object
    :param record: list The record itself, which will be modified in place
    :param acquire_time_i: int Index of the acquire time field
    """
    if not isinstance(record[acquire_time_i], datetime):
        record[acquire_time_i] = datetime.strptime(record[acquire_time_i], '%b %d, %Y %I:%M:%S %p')


def load_data(data_table, layout_pk, sheet_filename):
    import time
    time.sleep(4)
    return
    layout = Layout.objects.get(pk=layout_pk)

    data_table_iter = iter(data_table)
    headers = next(data_table_iter)
    data_keys = [h.strip().replace(' ', '_').replace('.', '').lower() for h in headers][1:]
    for record in data_table_iter:
        parse_acquire_time(record)
        quadrant = record[2][0]
        spot_code = record[3]
        bioentity = layout.bioentity_in_spot(quadrant, spot_code, dereference=False)

        SampleSpotData(
            bioentity=bioentity,
            from_file=sheet_filename,
            **dict(zip(data_keys, record[1:]))
        ).save()

