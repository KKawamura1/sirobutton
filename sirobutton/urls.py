from django.conf.urls import include, url
from django.urls import path
from django.contrib.sitemaps import views as sitemap_views
from django.contrib.sitemaps import Sitemap

from django.contrib import admin
admin.autodiscover()

from typing import NamedTuple, Mapping

from hello.views import index
from hello.urls import sitemaps as hello_sitemaps


class Application(NamedTuple):
    name: str
    sitemap: Mapping[str, Sitemap]


applications = [Application('hello', hello_sitemaps), ]

sitemaps = {
    '{}-{}'.format(app.name, key): sitemap
    for app in applications
    for key, sitemap in app.sitemap.items()
}

urlpatterns = [
    path('', index),
    path('sirobutton/', include('hello.urls')),
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}),
    path('sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]
