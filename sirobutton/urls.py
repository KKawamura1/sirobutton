from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import hello.views

urlpatterns = [
    url(r'^$', hello.views.SubtitleListView.as_view(), name='index'),
    path('lists/', hello.views.SubtitleListView.as_view(), name='lists'),
    path('subtitle/<int:pk>/', hello.views.SubtitleDetailView.as_view(), name='subtitle-detail'),
    path('jump-to-youtube/<int:pk>/', hello.views.RedirectToYoutubeView.as_view(),
         name='jump-to-youtube'),
    path('admin/', admin.site.urls),
]
