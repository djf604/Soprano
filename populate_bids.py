import os
import argparse

import django
from django.db.utils import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Soprano.settings')
django.setup()

from soprano.models import CaseIdToBidMapEntry, SampleCollection

parser = argparse.ArgumentParser()
parser.add_argument('--sheet')
parser.add_argument('--bid-col', default=2)
parser.add_argument('--case-col', default=3)
parser.add_argument('--collection-col', default=4)
parser.add_argument('--sep', default='\t')
args = vars(parser.parse_args())

with open(args['sheet']) as sheet:
    next(sheet), next(sheet), next(sheet)
    for line in sheet:
        bid, case_id, collection = [
            s.strip()
            for s in line.strip().split(args['sep'])[args['bid_col']:args['collection_col'] + 1]
        ]

        # Edge case for turning 22 to S-22
        if collection == 'SMRI "Extra"':
            case_id = 'S-{}'.format(case_id)

        # Edge case for N-2 vs N-02
        if collection == 'SMRI "New"':
            case_id = 'N-{}'.format(case_id.split('-')[1].zfill(2))

        sample_collection = SampleCollection.objects.get_or_create(name=collection)[0]

        CaseIdToBidMapEntry.objects.create(
            bid=bid,
            case_id=case_id.upper(),
            collection=sample_collection
        )
