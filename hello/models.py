from django.db import models


class Video(models.Model):
    video_id = models.CharField('youtube video id', max_length=20)
    title = models.CharField('video title', max_length=200)


class CaptionTrack(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    caption_id = models.CharField('youtube caption track id', max_length=20)
    language = models.CharField('caption language', max_length=20)


class Subtitle(models.Model):
    captiontrack = models.ForeignKey(CaptionTrack, on_delete=models.CASCADE)
    begin = models.TimeField('captions begin')
    end = models.TimeField('captions end')
    content = models.CharField('caption content', max_length=500)
