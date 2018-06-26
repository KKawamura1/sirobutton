from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpRequest, HttpResponse
from django.http import HttpResponseRedirect, HttpResponseGone, HttpResponsePermanentRedirect
from django.http import JsonResponse
from django.views import generic
from hitcount.views import HitCountDetailView, HitCountMixin
from hitcount.models import HitCount
import urllib.parse
from typing import List, Any, Dict, ClassVar
from logging import getLogger
import re

from .models import Video, CaptionTrack, Subtitle, Tag


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


class DetailedSearchView(generic.TemplateView):
    template_name = 'detailed_search.html'


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


class MyListViewWithPagination(generic.ListView):
    pages_around: ClassVar[int] = 1
    pages_edge: ClassVar[int] = 2

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['pages'] = type(self)._get_pages(context)
        return context

    @classmethod
    def _get_pages(cls, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        page_obj = context['page_obj']
        page_number = page_obj.number
        page_max = page_obj.paginator.num_pages

        # [1, 2], [...], [5, 6, 7], [8], [9, 10, 11], [...] [14, 15]
        # [edge] [elip] [around] [you_are_here] [around] [elip] [edge]

        # left
        rest_pages = page_number - 1
        # left around
        if rest_pages > 0:
            num = min(cls.pages_around, rest_pages)
            rest_pages -= num
            left_around_pages = [dict(type='around-left', number=(page_number-page-1), link=True)
                                 for page in range(num)][::-1]
        else:
            left_around_pages = []
        # left edge
        if rest_pages > 0:
            num = min(cls.pages_edge, rest_pages)
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
            num = min(cls.pages_around, rest_pages)
            rest_pages -= num
            right_around_pages = [dict(type='around-right', number=(page_number+page+1), link=True)
                                  for page in range(num)]
        else:
            right_around_pages = []
        # right edge
        if rest_pages > 0:
            num = min(cls.pages_edge, rest_pages)
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


class TagListView(MyListViewWithPagination):
    model = Tag
    context_object_name = 'tags'
    template_name = 'tag_list.html'
    paginate_by = 50
    ordering = ['-created_at']
    pages_around = 1
    pages_edge = 2


class SubtitleListView(MyListViewWithPagination):
    model = Subtitle
    context_object_name = 'subtitles'
    template_name = 'subtitle_list.html'
    paginate_by = 100
    ordering = ['hit_count_generic__hits', '-captiontrack__video__published', 'begin']
    pages_around = 1
    pages_edge = 2

    def get_queryset(self) -> Any:
        result_qs = super().get_queryset()
        # content search
        search_query = self.request.GET.get('search', '')
        search_targets = self._get_search_targets_from_query(search_query)
        if search_targets:
            search_targets = [re.escape(search_target) for search_target in search_targets]
            regex_query = r'.*{}.*'.format(r'.*'.join(search_targets))
            yomi_search = result_qs.filter(yomi__regex=regex_query)
            if yomi_search.exists():
                result_qs = yomi_search
            else:
                content_search = result_qs.filter(content__regex=regex_query)
                result_qs = content_search
        # tag search
        tag_search_query_encoded = self.request.GET.get('tag', '')
        tag_search_query = urllib.parse.unquote(tag_search_query_encoded)
        tag_search_targets = self._get_search_targets_from_query(tag_search_query)
        if tag_search_targets:
            for tag_search_target in tag_search_targets:
                result_qs = result_qs.filter(tags__title__exact=tag_search_target)
        # video search
        video_search_query = self.request.GET.get('video', '')
        video_search_targets = self._get_search_targets_from_query(video_search_query)
        if video_search_targets:
            video_search_targets = [re.escape(video_search_target)
                                    for video_search_target in video_search_targets]
            regex_query = r'.*{}.*'.format(r'.*'.join(video_search_targets))
            result_qs = result_qs.filter(captiontrack__video__title__regex=regex_query)
        return result_qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        searches = self._get_search_targets_from_query(search_query)
        tag_query = self.request.GET.get('tag', '')
        tag_searches = self._get_search_targets_from_query(tag_query)
        video_query = self.request.GET.get('video', '')
        video_searches = self._get_search_targets_from_query(video_query)
        context.update(dict(search_query=search_query, searches=searches,
                            tag_query=tag_query, tag_searches=tag_searches,
                            video_query=video_query, video_searches=video_searches))
        return context

    def _get_search_targets_from_query(self, search_query: str) -> List[str]:
        search_targets = search_query.split(' ')
        # remove invalid target
        search_targets = [search_target for search_target in search_targets if search_target]
        return search_targets


class PostAddTagView(generic.View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # get data in POST request
        tag_title = request.POST.get('tag_title')
        subtitle_id = request.POST.get('subtitle_id')
        # check whether the tag title is valid
        if not tag_title:
            return JsonResponse(dict(created=False, status_code=2,
                                     error_message='The tag title is blank.'))
        invalid_chars = set(['<', '>', '&', '"', "'", '`', ' '])
        used_invalid_chars = set(str(tag_title)) & invalid_chars
        if used_invalid_chars:
            error_message = 'Invalid character is used: {}'.format(used_invalid_chars)
            return JsonResponse(dict(created=False, status_code=3,
                                     error_message=error_message,
                                     used_invalid_chars=list(used_invalid_chars)))
        # make a tag with given info
        tag_target = dict(title=tag_title)
        tag, tag_created = Tag.objects.get_or_create(title=tag_title, defaults=tag_target)
        # get the subtitle
        subtitle = get_object_or_404(Subtitle, id=subtitle_id)
        # check whether the tag is already in the subtitle
        if subtitle.tags.all().filter(id__exact=tag.id).exists():
            return JsonResponse(dict(created=False, status_code=1,
                                     error_message='The tag is already in the subtitle.'))
        # add it to the subtitle
        try:
            subtitle.tags.add(tag)
            return JsonResponse(dict(created=True, status_code=0,
                                     error_message='Success.',
                                     tag_title=tag.title, tag_id=tag.id))
        except Exception as ext:
            error_message = 'Unexpected error is occurred. the error is: {}'.format(ext)
            return JsonResponse(dict(created=False, status_code=-1,
                                     error_message=error_message))


class PostRemoveTagView(generic.View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # get data in POST request
        tag_id = request.POST.get('tag_id')
        subtitle_id = request.POST.get('subtitle_id')
        # check the ids are valid
        tag = get_object_or_404(Tag, id=tag_id)
        subtitle = get_object_or_404(Subtitle, id=subtitle_id)
        # check if the tag is in the subtitle
        if not subtitle.tags.all().filter(id__exact=tag_id).exists():
            return JsonResponse(dict(removed=False, status_code=1,
                                     error_message='The tag is not in the subtitle.'))
        # remove the tag
        try:
            subtitle.tags.remove(tag)
            # also delete the tag if it has no associated subtitles
            if not tag.subtitle_set.all().exists():
                tag.delete()
            return JsonResponse(dict(removed=True, status_code=0,
                                     error_message='Success.',
                                     tag_title=tag.title))
        except Exception as ext:
            error_message = 'Unexpected error is occurred. the error is: {}'.format(ext)
            return JsonResponse(dict(removed=False, status_code=-1,
                                     error_message=error_message))
