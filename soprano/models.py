import numpy as np
import pandas as pd
from django.db import models


class Print(models.Model):
    name = models.CharField('Print Name', max_length=64, blank=True, null=True, unique=True)

    def as_dataframe(self, include_self=False):
        df = pd.concat([gel.as_dataframe(include=('antibody',)) for gel in self.gel_set.all()])
        if include_self:
            df.insert(0, 'print', self.name)
        return df


class Scan(models.Model):
    print = models.ForeignKey('Print')
    num = models.PositiveSmallIntegerField('Scan Number')

    def _get_name(self):
        return str(self.num)
    name = property(_get_name)

    def as_dataframe(self, include_self=False):
        df = pd.concat([gel.as_dataframe(include=('print', 'antibody')) for gel in self.gel_set.all()])
        if include_self:
            df.insert(0, 'scan', self.name)
        return df

    class Meta:
        unique_together = ('print', 'num')


class Gel(models.Model):
    print = models.ForeignKey('Print')
    scan = models.ForeignKey('Scan')
    antibody = models.ForeignKey('Antibody')
    data_sheet_filename = models.CharField('Data Sheet Filename', max_length=1024)

    class Meta:
        unique_together = ('print', 'antibody')

    def as_dataframe(self, include=None):
        gel_df = pd.DataFrame([s.as_list() for s in self.spotdata_set.all()], columns=SpotData.headers())
        if include is not None:
            for field in include[::-1]:
                gel_df.insert(0, field, getattr(self, field).name)
        return gel_df

    def get_data_by_spot(self, array, spot):
        return self.spotdata_set.get(array_name=array.upper(), spot_name=spot.upper())


class Antibody(models.Model):
    name = models.CharField('Antibody Name', max_length=64, unique=True)

    def as_dataframe(self, include_self=False):
        df = pd.concat([gel.as_dataframe(include=('print',)) for gel in self.gel_set.all()])
        if include_self:
            df.insert(0, 'antibody', self.name)
        return df


class Layout(models.Model):
    print = models.OneToOneField('Print')

    def bioentity_in_spot(self, array_name='A', spot='A1', dereference=True):
        bioen = self.layoutspot_set.filter(
            array_name=array_name.upper(),
            array_spot=spot.upper()
        ).first().bioentity
        return bioen.get() if dereference else bioen


class LayoutSpot(models.Model):
    layout = models.ForeignKey('Layout')

    # For the Google Sheets layout
    layout_row = models.CharField('Layout Row', max_length=2,
                                  help_text='')
    layout_column = models.IntegerField('Layout Column')

    # For the spot on the Gel
    array_name = models.CharField('Array Name', max_length=1,
                                  help_text='Array name as defined by ImageStudio')
    array_spot = models.CharField('Array Spot', max_length=4)
    bioentity = models.ForeignKey('BioEntity', on_delete=models.CASCADE)

    def __unicode__(self):
        return '{} | {}'.format(self.layout.print.name, ''.join((self.layout_row, str(self.layout_column))))

    def __str__(self):
        return self.__unicode__()


class BioEntity(models.Model):
    sample = models.ForeignKey('Sample', null=True, blank=True, on_delete=models.CASCADE)
    layout_constant = models.ForeignKey('LayoutConstant', null=True, blank=True, on_delete=models.CASCADE)

    def get(self):
        if self.sample:
            return self.sample
        elif self.layout_constant:
            return self.layout_constant
        else:
            raise ValueError('Bioentity is not set')


class Sample(models.Model):
    name = models.CharField('Sample Name', max_length=128, unique=True)
    print = models.ManyToManyField('Print')

    def as_dataframe(self, include_self=False):
        return pd.DataFrame([
            s.as_list(add_sample=include_self)
            for s in self.bioentity_set.first().spotdata_set.all()
        ], columns=SpotData.headers(add_sample=include_self))


class LayoutConstant(models.Model):
    name = models.CharField('Constant Name', max_length=64, unique=True)

    def __unicode__(self):
        return 'LayoutConstant {}'.format(self.name)

    def __str__(self):
        return self.__unicode__()


class SpotData(models.Model):
    gel = models.ForeignKey('Gel')
    bioentity = models.ForeignKey('BioEntity')

    # Directly from headers
    channel = models.CharField('Sample Data Channel', max_length=8)
    array_name = models.CharField('Sample Data Array', max_length=8)
    spot_name = models.CharField('Sample Data Spot Coordinate', max_length=8)
    signal = models.IntegerField('Sample Data Signal')
    total = models.IntegerField('Sample Data Total')
    area = models.IntegerField('Sample Data Area')
    bkgnd = models.IntegerField('Sample Data Bkgnd')
    type = models.CharField('Sample Data Type', max_length=128)
    acquire_time = models.DateTimeField('Sample Data Acquire Time')
    analysis = models.CharField('Sample Data Analysis', max_length=64)
    analysis_bkgnd_method = models.CharField('Sample Data Analysis Bkgnd Method', max_length=64)
    bkgnd_stddev = models.FloatField('Sample Data Bkgnd StdDev')
    concentration = models.CharField('Sample Data Concentration', max_length=128)
    height = models.IntegerField('Sample Data Height')
    intensities = models.CharField('Sample Data Intensities', max_length=64)
    max = models.IntegerField('Sample Data Max')
    resolution = models.CharField('Sample Data Resolution', max_length=64)
    stddev = models.FloatField('Sample Data StdDev')
    trim_signal = models.FloatField('Sample Data Trim Signal')
    trim_stddev = models.FloatField('Sample Data Trim StdDev')
    width = models.IntegerField('Sample Data Width')

    @classmethod
    def field_names(cls, only_data_fields=False):
        spotdata_field_names = [str(f).split('.')[-1] for f in cls._meta.get_fields()]
        if only_data_fields:
            return spotdata_field_names[spotdata_field_names.index('channel'):]
        return spotdata_field_names

    @classmethod
    def headers(cls, add_sample=True):
        if add_sample:
            return ['sample'] + cls.field_names(only_data_fields=True)
        return cls.field_names(only_data_fields=True)

    def as_dataframe(self, add_sample=True):
        # Get the field names for channel through width
        data_fields = SpotData.field_names(only_data_fields=True)
        data = np.array(SpotData.objects.values_list(*data_fields).get(pk=self.pk))
        if add_sample:
            data = np.insert(data, 0, self.bioentity.get().name)
            data_fields.insert(0, 'sample')

        return pd.DataFrame([data], columns=data_fields)

    def as_list(self, acquire_time_to_str=False, add_sample=True):
        # Get the field names for channel through width
        data_fields = SpotData.field_names(only_data_fields=True)

        # Extract data based on field names
        spotdata_data = list(SpotData.objects.values_list(*data_fields).get(pk=self.pk))

        # If acquire_time should be str, convert in place
        if acquire_time_to_str:
            acquire_time_i = data_fields.index('acquire_time')
            acquire_time = spotdata_data[acquire_time_i]
            spotdata_data[acquire_time_i] = acquire_time.strftime('%b %d, %Y %I:%M:%S %p')

        # Add Bioentity name to front, return as a list
        if add_sample:
            return [self.bioentity.get().name] + spotdata_data
        return spotdata_data
