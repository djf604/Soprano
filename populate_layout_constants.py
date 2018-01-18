import os

import django
from django.db.utils import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Soprano.settings')
django.setup()

from soprano.models import LayoutConstant

for constant in ['L', 'PL', 'BLANK', 'REF1', 'REF2', 'REF3']:
    try:
        LayoutConstant(name=constant).save()
    except IntegrityError:
        print('Layout Constant {} already exists'.format(constant))
    except Exception:
        print('Something else went wrong adding {}'.format(constant))
