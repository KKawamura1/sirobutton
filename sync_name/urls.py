from django.urls import path

import sync_name.views


app_name = 'sync_name'

urlpatterns = [
    path('', sync_name.views.GetOAuthView.as_view(), name='get_oauth'),
    path('after_oauth/', sync_name.views.AfterOAuthView.as_view(), name='after_oauth'),
    path('settings/<int:pk>/', sync_name.views.Settings.as_view(), name='settings'),
    path('api/v1/get_oauth/', sync_name.views.APIGetOAuthView.as_view(), name='api_get_oauth'),
    path('api/v1/update_all/', sync_name.views.UpdateAllAPI.as_view(), name='api_update_all'),
]
