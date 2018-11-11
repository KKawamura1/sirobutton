from django.urls import path

import sync_user_name.views


app_name = 'sync_name'

urlpatterns = [
    path('api/v1/update', sync_user_name.views.)
]