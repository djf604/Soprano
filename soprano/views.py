import uuid

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from pyexcel.exceptions import FileTypeNotSupported
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.html import escape

import soprano.util
from soprano.models import Layout
from soprano.util import normalize_sheet_file

from soprano.models import Print, Scan, Sample, Antibody
from soprano.uploaders import print_layout_uploader, technical_data_uploader
from soprano import gatherers

# Create your views here.


class FrontEnd(object):
    class Home(View):
        def get(self,request):
            context = {
                'layouts': Layout.objects.all()
            }
            return render(request, 'soprano/home.html', context)

    class HandleTechnicalDataUpload(LoginRequiredMixin, View):
        def get(self, request):
            context = {
                'prints': Print.objects.all()
            }
            return render(request, 'soprano/add_technical_data.html', context)

        def post(self, request):
            normalized_sheet = normalize_sheet_file(request.FILES['upload-file'])
            if normalized_sheet is not None:
                try:
                    technical_data_uploader(
                        sheet=normalized_sheet,
                        print_pk=request.POST['print-pk'],
                        scan_number=int(request.POST['scan-number']),
                        sheet_filename=str(request.FILES['upload-file'])
                    )
                    messages.info(request, 'Data from {} was successfully put into the database.'.format(
                        str(request.FILES['upload-file'])
                    ))
                except Exception as e:
                    messages.info(request, 'There was an error uploading data from {}<br/> Error: {}'.format(
                        str(request.FILES['upload-file']),
                        escape(str(e))
                    ))
            else:
                messages.info(request, 'There was an error normalizing {}'.format(
                    str(request.FILES['upload-file'])
                ))
            return HttpResponseRedirect(reverse_lazy('index'))

    class HandlePrintUpload(LoginRequiredMixin, View):
        def get(self, request):
            return render(request, 'soprano/add_print.html')

        def post(self, request):
            normalized_sheet = normalize_sheet_file(request.FILES['upload-file'])
            if normalized_sheet is not None:
                try:
                    print_layout_uploader(normalized_sheet, request.POST['print-name'])
                    messages.info(request, 'Print {} successfully uploaded'.format(request.POST['print-name']))
                except Exception as e:
                    messages.info(request, 'There was an error uploading {}<br/> Error: {}'.format(
                        request.POST['print-name'],
                        escape(str(e))
                    ))
            return HttpResponseRedirect(reverse_lazy('index'))

    class HandleDataDownload(LoginRequiredMixin, View):
        def get(self, request):
            context = {
                'samples': sorted(Sample.objects.all(), key=lambda r: r.name),
                'antibodies': Antibody.objects.all(),
                'prints': Print.objects.all(),
                'scans': Scan.objects.all()
            }
            return render(request, 'soprano/download_sheet.html', context)

        def post(self, request):
            uuid_tag = str(uuid.uuid4())[:8]
            filter_type = request.POST['filter-type']
            if filter_type == 'get-all':
                df = gatherers.get_all()
                filename = 'All_RPPA_data_{}.csv'.format(uuid_tag)
            elif filter_type == 'by-sample':
                df = gatherers.by_sample(
                    sample_name=request.POST['by-sample-name'],
                    include_self='by-sample-include-self' in request.POST
                )
                filename = 'Sample_{}_RPPA_data_{}.csv'.format(request.POST['by-sample-name'], uuid_tag)
            elif filter_type == 'by-antibody':
                df = gatherers.by_antibody(
                    antibody_name=request.POST['by-antibody-name'],
                    include_self='by-antibody-include-self' in request.POST
                )
                filename = 'Antibody_{}_RPPA_data_{}.csv'.format(request.POST['by-antibody-name'], uuid_tag)
            elif filter_type == 'by-gel':
                include_as_columns = [
                    e
                    for e in ('print', 'antibody', 'scan')
                    if 'by-gel-include-' + e in request.POST
                ]
                df = gatherers.by_gel(
                    print_name=request.POST['by-gel-print-name'],
                    antibody_name=request.POST['by-gel-antibody-name'],
                    include=include_as_columns
                )
                filename = 'Gel_{}_{}_RPPA_data_{}.csv'.format(
                    request.POST['by-gel-print-name'],
                    request.POST['by-gel-antibody-name'],
                    uuid_tag
                )
            elif filter_type == 'by-print':
                df = gatherers.by_print(
                    print_name=request.POST['by-print-name'],
                    include_self='by-print-include-self' in request.POST
                )
                filename = 'Print_{}_RPPA_data_{}.csv'.format(request.POST['by-print-name'], uuid_tag)
            else:  # by-scan
                df = gatherers.by_scan_pk(
                    scan_pk=request.POST['by-scan-pk'],
                    include_self='by-scan-include-self' in request.POST
                )
                scan = Scan.objects.get(pk=request.POST['by-scan-pk'])
                filename = 'Scan_{}_{}_RPPA_data_{}.csv'.format(scan.print.name, scan.num, uuid_tag)

            response = HttpResponse(content_type='text/csv')
            response['X-Filename'] = filename
            response.write(df.to_csv(index=None))
            return response
