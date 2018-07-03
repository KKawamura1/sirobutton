from typing import Any
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from hitcount.models import HitCount, HitCountMixin


class Video(models.Model):
    id = models.AutoField(primary_key=True)
    video_id = models.CharField('youtube video id', max_length=50)
    title = models.CharField('video title', max_length=500)
    published = models.DateTimeField('video published')
    last_updated = models.DateTimeField('last modified time', auto_now=True)

    def __str__(self) -> str:
        return '<Video: {}>'.format(self.title)


class CaptionTrack(models.Model):
    id = models.AutoField(primary_key=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    caption_id = models.CharField('youtube caption track id', max_length=50)
    language = models.CharField('caption language', max_length=20)
    last_updated = models.DateTimeField('last modified time', auto_now=True)

    def __str__(self) -> str:
        return '<CaptionTrack of {}, language: {}>'.format(self.video, self.language)


class Tag(models.Model):
    title = models.CharField('tag title', max_length=100)
    created_at = models.DateTimeField('tag created time', auto_now_add=True)

    def __str__(self) -> str:
        return '<Tag: {}>'.format(self.title)


class Subtitle(models.Model, HitCountMixin):
    id = models.AutoField(primary_key=True)
    captiontrack = models.ForeignKey(CaptionTrack, on_delete=models.CASCADE)
    begin = models.TimeField('captions begin')
    end = models.TimeField('captions end')
    content = models.CharField('caption content', max_length=500)
    short_title = models.CharField('short version of caption content', max_length=50)
    yomi = models.CharField('hiragana yomi for the content', max_length=500)
    last_updated = models.DateTimeField('last modified time', auto_now=True)
    # enable flag (disable if it was on the old caption track but not in the new)
    enable = models.BooleanField('enable flag', default=True)
    # frozen flag (enable if it requires living even if it is not in the new caption tracks)
    frozen = models.BooleanField('frozen flag', default=False)

    # see: http://django-hitcount.readthedocs.io/en/latest/installation.html#models
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    # many-to-many relation
    tags = models.ManyToManyField(Tag)

    def __str__(self) -> str:
        return '<Subtitle: {}>'.format(self.content)
