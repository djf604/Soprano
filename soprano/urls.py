from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from soprano.views import FrontEnd

urlpatterns = [
    url(r'^$', FrontEnd.Home.as_view(), name='index'),
    url(r'^upload-tech-data/$', FrontEnd.HandleTechnicalDataUpload.as_view(), name='upload_tech_data'),
    url(r'^upload-print/$', FrontEnd.HandlePrintUpload.as_view(), name='upload_print'),
    url(r'^download-sheet/$', FrontEnd.HandleDataDownload.as_view(), name='download_sheet'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='soprano/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]
