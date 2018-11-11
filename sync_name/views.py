from django.http import HttpRequest, HttpResponse
from django.views import generic
from typing import Any
from


class DoSyncView(generic.View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pass

    @classmethod
    def do_sync(cls, ):