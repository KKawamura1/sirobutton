from django.contrib import admin
from .models import Video, CaptionTrack, Subtitle, Tag

# register my models to change it on admin console

admin.site.register(Video)
admin.site.register(CaptionTrack)
admin.site.register(Subtitle)
admin.site.register(Tag)
