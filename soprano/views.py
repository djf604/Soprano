from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages
from pyexcel.exceptions import FileTypeNotSupported

import soprano.util
from soprano.models import Layout
from soprano.util import normalize_sheet_file

from soprano.models import Print
from soprano.uploaders import print_layout_uploader, technical_data_uploader

# Create your views here.


class FrontEnd(object):
    class Home(View):
        def get(self,request):
            context = {
                'layouts': Layout.objects.all()
            }
            return render(request, 'soprano/home.html', context)

    class HandleTechnicalDataUpload(View):
        def get(self, request):
            context = {
                'prints': Print.objects.all()
            }
            return render(request, 'soprano/add_technical_data.html', context)

        def post(self, request):
            normalized_sheet = normalize_sheet_file(request.FILES['upload-file'])
            if normalized_sheet is not None:
                technical_data_uploader(
                    sheet=normalized_sheet,
                    print_pk=request.POST['print-pk'],
                    scan_number=int(request.POST['scan-number']),
                    sheet_filename=str(request.FILES['upload-file'])
                )
                messages.add_message(request, messages.INFO, 'Data from {} was successfully put into the database.'.format(
                    str(request.FILES['upload-file'])
                ))
            return HttpResponseRedirect('/')

    class HandlePrintUpload(View):
        def post(self, request):
            normalized_sheet = normalize_sheet_file(request.FILES['upload-file'])
            if normalized_sheet is not None:
                print_layout_uploader(normalized_sheet, request.POST['print-name'])
            return HttpResponseRedirect('/')
