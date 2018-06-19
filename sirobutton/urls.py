from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import hello.views

urlpatterns = [
    url(r'^$', hello.views.IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
]
