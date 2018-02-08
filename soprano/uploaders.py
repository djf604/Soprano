import os
import math
from soprano.models import (LayoutConstant, Layout, LayoutSpot, BioEntity, Sample, Print,
                            Antibody, Gel, Scan, SpotData, CaseIdToBidMapEntry)
from soprano.util import parse_acquire_time

LAYOUT_TABLE_SLICE = slice(5, 22)
ACQUIRE_TIME_I = 9
ARRAY_NAME = 2
FIRST_CHAR = 0
SPOT_CODE = 3


def print_layout_uploader(sheet, print_name):
    mohana_imagestudio_map = {'A': 'A', 'C': 'B', 'E': 'C', 'G': 'D'}
    layout_constants = {l.name for l in LayoutConstant.objects.all()}

    print_ = Print(name=print_name)
    print_.save()

    layout = Layout(print=print_)
    layout.save()

    sheet_rows = iter(sheet)
    layout_rows = 'ACEG'
    for layout_row in layout_rows:
        _, _, spots = next(sheet_rows), next(sheet_rows), next(sheet_rows)[LAYOUT_TABLE_SLICE]
        for layout_col, spot_value in enumerate(spots, start=1):
            spot_value = spot_value.strip()

            # Check if this value is a constant
            if spot_value in layout_constants:
                spot_bioentity = BioEntity(layout_constant=LayoutConstant.objects.get(name=spot_value))
            else:
                # This value is a real sample
                try:
                    bid = CaseIdToBidMapEntry.objects.get(case_id=spot_value.strip().upper()).bid
                except CaseIdToBidMapEntry.DoesNotExist:
                    # Abort and roll back everything
                    print_.delete()
                    print('{} does not exist'.format(spot_value))
                    raise

                sample = Sample.objects.get_or_create(name=bid, case_id=spot_value.strip().upper())[0]
                sample.print.add(print_)
                sample.save()
                spot_bioentity = BioEntity(sample=sample)
            spot_bioentity.save()

            # Calculate grid quadrant and spot location
            array_name = mohana_imagestudio_map[layout_row]
            # Take care of edge case of position 17
            array_column = str(math.ceil(layout_col / 2.0))
            if layout_col % 2 == 0 or layout_col == 17:  # If sheet_col is even numbered or equals 17
                array_row_letters = 'EFGH'
            else:  # If sheet_col is odd numbered
                array_row_letters = 'ABCD'

            for array_row_letter in array_row_letters:
                LayoutSpot(
                    layout=layout,
                    layout_row=layout_row,
                    layout_column=layout_col,
                    array_name=array_name,
                    array_spot=''.join((array_row_letter, array_column)),
                    bioentity=spot_bioentity
                ).save()


def technical_data_uploader(sheet, print_pk, scan_number, sheet_filename):
    print_ = Print.objects.get(pk=print_pk)
    layout = print_.layout

    # Get name of antibody used from 2nd row, 1st col, second half of split on '-'
    antibody_used = sheet[1][0].strip().split('-')[1]

    gel = Gel.objects.create(
        print=print_,
        scan=Scan.objects.get_or_create(print=print_, num=int(scan_number))[0],
        antibody=Antibody.objects.get_or_create(name=antibody_used)[0],
        data_sheet_filename=os.path.basename(sheet_filename)
    )

    sheet_iter = iter(sheet)
    data_keys = [h.strip().replace(' ', '_').replace('.', '').lower() for h in next(sheet_iter)][1:]
    for record in sheet_iter:
        parse_acquire_time(record, acquire_time_i=ACQUIRE_TIME_I)
        record[ARRAY_NAME] = record[ARRAY_NAME][FIRST_CHAR]
        bioentity = layout.bioentity_in_spot(record[ARRAY_NAME], record[SPOT_CODE], dereference=False)

        SpotData.objects.create(
            gel=gel,
            bioentity=bioentity,
            **dict(zip(data_keys, record[1:]))
        )
