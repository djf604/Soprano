import pandas as pd
from soprano.models import Print, Antibody, Scan, Gel, Sample


def by_print(print_name, include_self=False):
    return Print.objects.get(name=print_name).as_dataframe(include_self)


def by_antibody(antibody_name, include_self=False):
    return Antibody.objects.get(name=antibody_name).as_dataframe(include_self)


def by_scan_pk(scan_pk, include_self=False):
    return Scan.objects.get(pk=scan_pk).as_dataframe(include_self)


def by_gel(print_name, antibody_name, include):
    return Gel.objects.get(print__name=print_name, antibody__name=antibody_name).as_dataframe(include)


def by_sample(sample_name, include_self=False):
    return Sample.objects.get(name=sample_name).as_dataframe(include_self)


def get_all():
    return pd.concat([
        gel.as_dataframe(include=('print', 'antibody', 'scan'))
        for gel in Gel.objects.all()
    ])
