import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Soprano.settings')
django.setup()

from pyexcel.sheet import Sheet
from soprano.uploaders import print_layout_uploader
from django.db.utils import IntegrityError

layouts_dir = '/home/dfitzgerald/projects/PsychENCODE/RPPA/Layouts'
for layout in os.listdir(layouts_dir):
    layout_name = layout.split('.')[0]
    layout_matrix = [line.strip('\n').split('\t') for line in open(os.path.join(layouts_dir, layout))]
    print(layout)
    sheet = Sheet(layout_matrix)
    try:
        print_layout_uploader(sheet, layout_name)
    except IntegrityError:
        pass
