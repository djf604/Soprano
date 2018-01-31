from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from soprano.views import FrontEnd

urlpatterns = [
    url(r'^$', FrontEnd.Home.as_view()),
    url(r'^upload-tech-data/$', FrontEnd.HandleTechnicalDataUpload.as_view()),
    url(r'^upload-print/$', FrontEnd.HandlePrintUpload.as_view()),
    url(r'^download-sheet/$', FrontEnd.HandleDataDownload.as_view()),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='soprano/login.html')),
    url(r'^logout/$', auth_views.LogoutView.as_view()),
]
