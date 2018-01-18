from django.conf.urls import url
from django.views.generic import TemplateView

from soprano.views import FrontEnd

urlpatterns = [
    url(r'^$', FrontEnd.Home.as_view()),
    url(r'^upload-tech-data/$', FrontEnd.HandleTechnicalDataUpload.as_view()),
    url(r'^add-print/$', TemplateView.as_view(template_name='soprano/add_print.html')),
    url(r'^upload-print/$', FrontEnd.HandlePrintUpload.as_view()),
]
