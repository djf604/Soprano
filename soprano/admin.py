from django.contrib import admin
from soprano.models import (LayoutConstant, Print, Scan, Gel, Antibody, Layout, LayoutSpot,
                            BioEntity, Sample, SampleCollection, CaseIdToBidMapEntry, SpotData)

# Register your models here.
admin.site.register(Print)
admin.site.register(Scan)
admin.site.register(Gel)
admin.site.register(Antibody)
admin.site.register(Layout)
admin.site.register(LayoutSpot)
admin.site.register(BioEntity)
admin.site.register(Sample)
admin.site.register(SampleCollection)
admin.site.register(CaseIdToBidMapEntry)
admin.site.register(SpotData)
admin.site.register(LayoutConstant)
