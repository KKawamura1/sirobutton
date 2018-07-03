from django.core.management.base import BaseCommand
from typing import Any
from tqdm import tqdm

from hello.models import Subtitle
from hitcount.models import HitCount


class Command(BaseCommand):
    help = 'add count-hit object to fix ordering'

    def handle(self, *args: Any, **options: Any) -> None:
        no_hit_count_subtitles = Subtitle.objects.exclude(hit_count_generic__hits__gt=0)
        no_hit_count_subtitles = no_hit_count_subtitles.exclude(hit_count_generic__hits__exact=0)
        for no_hit_count_subtitle in tqdm(no_hit_count_subtitles):
            _ = HitCount.objects.get_for_object(no_hit_count_subtitle)
