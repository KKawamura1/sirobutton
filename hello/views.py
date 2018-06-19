from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views import generic
from typing import List

from .models import Video, CaptionTrack, Subtitle

# Create your views here.


def index(request: HttpRequest) -> HttpResponse:
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'subtitle_list'

    def get_queryset(self):
        """Return subtitles."""
        return Subtitle.objects.all()
