from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import admin
from django.urls import path

from django.urls.conf import include

urlpatterns = [
    path('', lambda r: HttpResponseRedirect("liveFeed/detect")),
    path('liveFeed/', include('LivCam.urls')),
    path('admin/', admin.site.urls),
]