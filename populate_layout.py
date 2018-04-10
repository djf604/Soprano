import os
import argparse
import math

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Soprano.settings')
django.setup()

from soprano.models import Layout, LayoutSpot, LayoutConstant, Sample, BioEntity, Print

LAYOUT_TABLE_SLICE = slice(5, 22)
mohana_imagestudio_map = {
    'A': 'A',
    'C': 'B',
    'E': 'C',
    'G': 'D'
}

parser = argparse.ArgumentParser()
parser.add_argument('--sheet')
parser.add_argument('--print-name')
args = vars(parser.parse_args())

layout_constants = {l.name for l in LayoutConstant.objects.all()}
print_ = Print.objects.get_or_create(name=args['print_name'])[0]
print_.save()
layout = Layout(print=print_)
layout.save()

layout_rows = 'ACEG'
with open(args['sheet']) as sheet:
    for layout_row in layout_rows:
        next(sheet), next(sheet)
        record = next(sheet).strip().split('\t')
        spots = record[LAYOUT_TABLE_SLICE]
        for layout_col, spot_value in enumerate(spots, start=1):
            spot_value = spot_value.strip()

            # Check if this value is a constant
            if spot_value in layout_constants:
                spot_bioentity = BioEntity(layout_constant=LayoutConstant.objects.get(name=spot_value))
            else:
                spot_bioentity = BioEntity(sample=Sample.objects.get_or_create(name=spot_value)[0])
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

            # Add blanks to Spots A9-D9
            for array_row_letter in 'ABCD':
                spot_bioentity = BioEntity(layout_constant=LayoutConstant.objects.get(name='BLANK'))
                spot_bioentity.save()
                LayoutSpot(
                    layout=layout,
                    layout_row=layout_row,
                    layout_column=-1,
                    array_name=array_name,
                    array_spot=''.join((array_row_letter, '9')),
                    bioentity=spot_bioentity
                ).save()
