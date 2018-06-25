from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpRequest, HttpResponse
from django.http import HttpResponseRedirect, HttpResponseGone, HttpResponsePermanentRedirect
from django.views import generic
from hitcount.views import HitCountDetailView, HitCountMixin
from hitcount.models import HitCount
import urllib.parse
from typing import List, Any, Dict
from logging import getLogger

from .models import Video, CaptionTrack, Subtitle


logger = getLogger('__name__')


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponsePermanentRedirect(reverse('sirobutton:home'))


class SubtitleDetailView(HitCountDetailView):
    model = Subtitle
    context_object_name = 'subtitle'
    template_name = 'subtitle_detail.html'
    count_hit = True

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        subtitle: Subtitle = context['subtitle']
        context['subtitle_time'] = {key: time.hour * 3600 + time.minute * 60 + time.second
                                    for key, time in [('begin', subtitle.begin),
                                                      ('end', subtitle.end)]}
        context['subtitle_time']['end'] += 1
        return context


class RedirectToYoutubeView(generic.View):
    url_base = 'https://www.youtube.com/watch'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        url = self.get_redirect_url_with_request(request, *args, **kwargs)
        if url:
            return HttpResponseRedirect(url)
        else:
            return HttpResponseGone()

    def head(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def options(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def put(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def patch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def get_redirect_url_with_request(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any
    ) -> str:
        subtitle = get_object_or_404(Subtitle, pk=kwargs['pk'])
        self._countup_subtitle(request, subtitle)
        video_id = subtitle.captiontrack.video.video_id
        begin = subtitle.begin
        begin_as_str = '{}h{}m{}s'.format(begin.hour, begin.minute, begin.second)
        queries = dict(v=video_id, t=begin_as_str)
        url = type(self).url_base + '?' + urllib.parse.urlencode(queries)
        return url

    def _countup_subtitle(self, request: HttpRequest, subtitle: Subtitle) -> None:
        hit_count = HitCount.objects.get_for_object(subtitle)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        if not hit_count_response.hit_counted:
            logger.info('hit count failed: {}'.format(hit_count_response))


class SubtitleListView(generic.ListView):
    model = Subtitle
    context_object_name = 'subtitles'
    template_name = 'subtitle_list.html'
    paginate_by = 100
    ordering = ['hit_count_generic__hits', '-captiontrack__video__published', 'begin']
    pages_around = 1
    pages_edge = 2

    def get_queryset(self) -> Any:
        queryset = super().get_queryset()
        search_target = self.request.GET.get('search', '')
        if queryset.filter(yomi__contains=search_target).exists():
            result_qs = queryset.filter(yomi__contains=search_target)
        else:
            result_qs = queryset.filter(content__contains=search_target)
        return result_qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['pages'] = self._get_pages(context)
        context['search_box'] = self.request.GET.get('search', '')
        return context

    def _get_pages(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        page_obj = context['page_obj']
        page_number = page_obj.number
        page_max = page_obj.paginator.num_pages

        # [1, 2], [...], [5, 6, 7], [8], [9, 10, 11], [...] [14, 15]
        # [edge] [elip] [around] [you_are_here] [around] [elip] [edge]

        # left
        rest_pages = page_number - 1
        # left around
        if rest_pages > 0:
            num = min(SubtitleListView.pages_around, rest_pages)
            rest_pages -= num
            left_around_pages = [dict(type='around-left', number=(page_number-page-1), link=True)
                                 for page in range(num)][::-1]
        else:
            left_around_pages = []
        # left edge
        if rest_pages > 0:
            num = min(SubtitleListView.pages_edge, rest_pages)
            rest_pages -= num
            left_edge_pages = [dict(type='edge-left', number=(page+1), link=True)
                               for page in range(num)]
        else:
            left_edge_pages = []
        # left ellipsis
        if rest_pages > 0:
            left_ellip = [dict(type='ellip-left', link=False)]
        else:
            left_ellip = []

        # right
        rest_pages = page_max - page_number
        # right around
        if rest_pages > 0:
            num = min(SubtitleListView.pages_around, rest_pages)
            rest_pages -= num
            right_around_pages = [dict(type='around-right', number=(page_number+page+1), link=True)
                                  for page in range(num)]
        else:
            right_around_pages = []
        # right edge
        if rest_pages > 0:
            num = min(SubtitleListView.pages_edge, rest_pages)
            rest_pages -= num
            right_edge_pages = [dict(type='edge-right', number=(page_max-page), link=True)
                                for page in range(num)][::-1]
        else:
            right_edge_pages = []
        # right ellipsis
        if rest_pages > 0:
            right_ellip = [dict(type='ellip-right', link=False)]
        else:
            right_ellip = []

        # you_are_here
        you_are_here = [dict(type='you_are_here', number=page_number, link=False)]

        pages = (left_edge_pages + left_ellip + left_around_pages
                 + you_are_here
                 + right_around_pages + right_ellip + right_edge_pages)
        return pages
