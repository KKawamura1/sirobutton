from django.db import models


class Video(models.Model):
    video_id = models.CharField('youtube video id', max_length=20)
    title = models.CharField('video title', max_length=200)

    def __str__(self) -> str:
        return '<Video: {}>'.format(self.title)


class CaptionTrack(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    caption_id = models.CharField('youtube caption track id', max_length=20)
    language = models.CharField('caption language', max_length=20)

    def __str__(self) -> str:
        return '<CaptionTrack of {}, language: {}>'.format(self.video, self.language)


class Subtitle(models.Model):
    captiontrack = models.ForeignKey(CaptionTrack, on_delete=models.CASCADE)
    begin = models.TimeField('captions begin')
    end = models.TimeField('captions end')
    content = models.CharField('caption content', max_length=500)

    def __str__(self) -> str:
        return '<Subtitle: {}>'.format(self.content)
