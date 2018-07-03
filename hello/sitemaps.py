from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from typing import Any, List
from datetime import datetime

from hello.models import Subtitle, Tag


QuerySet = Any


class SubtitleSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5
    limit = 10000

    def items(self) -> QuerySet:
        return Subtitle.objects.filter(enable=True)

    def lastmod(self, subtitle: Subtitle) -> datetime:
        return subtitle.last_updated


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self) -> List[str]:
        return ['home', 'lists', 'tags', 'detailed-search', 'about-this']

    def location(self, item: str) -> str:
        return reverse('sirobutton:{}'.format(item))
