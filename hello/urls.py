from django.urls import path
from django.contrib.sitemaps.views import sitemap

import hello.views
from hello.sitemaps import SubtitleSitemap, StaticSitemap

app_name = 'sirobutton'

sitemaps = {
    'subtitles': SubtitleSitemap,
    'static': StaticSitemap,
}

urlpatterns = [
    path('', hello.views.SubtitleListView.as_view(), name='home'),
    path('lists/', hello.views.SubtitleListView.as_view(), name='lists'),
    path('subtitle/<int:pk>/', hello.views.SubtitleDetailView.as_view(), name='subtitle-detail'),
    path('tags/', hello.views.TagListView.as_view(), name='tags'),
    path('extra-search/', hello.views.DetailedSearchView.as_view(), name='detailed-search'),
    path('about-this/', hello.views.AboutThisView.as_view(), name='about-this'),
    path('jump-to-youtube/<int:pk>/', hello.views.RedirectToYoutubeView.as_view(),
         name='jump-to-youtube'),
    path('api/v1/post-add-tag/', hello.views.PostAddTagView.as_view(), name='add-tag'),
    path('api/v1/post-remove-tag/', hello.views.PostRemoveTagView.as_view(), name='remove-tag'),
    path('api/v1/oembed/', hello.views.OEmbedView.as_view(), name='oembed'),
]
