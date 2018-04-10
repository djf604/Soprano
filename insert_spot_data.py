"""
Should be used in the root of a file structure that looks like:

(soprano) dfitzgerald@dfitzgerald:~/projects/PsychENCODE/RPPA/Drive_csv/Drive$ ls
RPPA10  RPPA12  RPPA14  RPPA16  RPPA18  RPPA20  RPPA22  RPPA24  RPPA26  RPPA4  RPPA6  RPPA8
RPPA11  RPPA13  RPPA15  RPPA17  RPPA19  RPPA21  RPPA23  RPPA25  RPPA27  RPPA5  RPPA7  RPPA9

"""
import os
import sys
import traceback

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Soprano.settings')
django.setup()

from soprano.models import Print, SpotData, Scan, Gel, Antibody
from django.db import transaction

FIRST_CHAR = 0


@transaction.atomic
def insert_spot_data(sheet_path, print_name, scan_num):
    print_ = Print.objects.get(name=print_name)
    layout = print_.layout

    with open(sheet_path) as sheet:
        headers = next(sheet).strip().split(',')
        antibody_used = next(sheet).strip().split(',')[headers.index('Image Name')].split('_')[1]
        data_keys = [h.strip().replace(' ', '_').replace('.', '').lower() for h in headers[1:]]

        # Create the gel object
        gel = Gel.objects.create(
            print=print_,
            scan=Scan.objects.get_or_create(print=print_, num=scan_num)[0],
            antibody=Antibody.objects.get_or_create(name=antibody_used)[0],
            data_sheet_filename=os.path.basename(sheet_path)
        )

        # Get index of needed headers
        array_name_i = data_keys.index('array_name') + 1
        spot_name_i = data_keys.index('spot_name') + 1

        # Seek to beginning of file, then throw away header line
        sheet.seek(0)
        next(sheet)
        for record in sheet:
            record = record.strip().split(',')
            record[array_name_i] = record[array_name_i][FIRST_CHAR]
            bioentity = layout.bioentity_in_spot(record[array_name_i], record[spot_name_i], dereference=False)

            # Create SpotData for this row
            SpotData.objects.create(
                gel=gel,
                bioentity=bioentity,
                **dict(zip(data_keys, record[1:]))
            )


def main():
    # Check that root has the correct format
    if not all(['RPPA' in rppa_dir for rppa_dir in os.listdir('.')]):
        print('Root structure is incorrect')
        sys.exit()

    # Walk file structure and upload all data
    uploaded_files, total = 0, 0
    errors = list()
    for root, dirs, files in os.walk('.'):
        if files:
            print_name = root.split('/')[-2]
            scan_num = int(root.split('/')[-1].replace('SCAN', ''))

            for sheet_path in files:
                total += 1
                print('Attemping upload of file {} [{}]'.format(total, os.path.join(root, sheet_path)))
                try:
                    insert_spot_data(os.path.join(root, sheet_path), print_name, scan_num)
                    uploaded_files += 1
                except Exception as e:
                    traceback.print_exception(*sys.exc_info())
                    errors.append(os.path.join(root, sheet_path))

    print('Uploaded {}/{}'.format(uploaded_files, total))
    print('Errors:')
    for error in errors:
        print('\t{}'.format(error))


if __name__ == '__main__':
    main()
