from django.conf.urls import url
from .views import feed, detect, scan
from django.urls import path

app_name = 'LivCam'

urlpatterns = [
    url("feed/", feed, name='live-feed'),
    url("detect/", detect, name='live-detect'),
    url("scan/", scan, name="live-scan"),
]
