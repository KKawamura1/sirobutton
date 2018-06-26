from django.urls import path

import hello.views

app_name = 'sirobutton'
urlpatterns = [
    path('', hello.views.SubtitleListView.as_view(), name='home'),
    path('lists/', hello.views.SubtitleListView.as_view(), name='lists'),
    path('subtitle/<int:pk>/', hello.views.SubtitleDetailView.as_view(), name='subtitle-detail'),
    path('tags/', hello.views.TagListView.as_view(), name='tags'),
    path('jump-to-youtube/<int:pk>/', hello.views.RedirectToYoutubeView.as_view(),
         name='jump-to-youtube'),
    path('api/v1/post-add-tag/', hello.views.PostAddTagView.as_view(), name='add-tag'),
    path('api/v1/post-remove-tag/', hello.views.PostRemoveTagView.as_view(), name='remove-tag'),
]
