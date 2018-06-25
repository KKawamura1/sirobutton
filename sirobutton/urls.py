from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

from hello.views import index


urlpatterns = [
    path('', index),
    path('sirobutton/', include('hello.urls')),
    path('admin/', admin.site.urls),
]
