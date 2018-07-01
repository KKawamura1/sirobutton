from logging import getLogger, Logger
from typing import List
import requests

from ..models import VideoInfo, CaptionInfo, Caption
from .treat_webvtt import webvtt_string_to_parsed


class DirtyYoutubeAPI:
    def __init__(self, logger: Logger = getLogger(__name__)) -> None:
        self._logger = logger

    def download_caption(
            self,
            target_video_info: VideoInfo,
            target_caption_info: CaptionInfo
    ) -> List[Caption]:
        target_video_id = target_video_info.video_id
        target_language = 'ja'
        target_caption_name = target_caption_info.name

        timedtext_api = 'https://www.youtube.com/api/timedtext'
        # get captions
        request_captions = dict(fmt='vtt', v=target_video_id, lang=target_language)
        if target_caption_name != '':
            request_captions['name'] = target_caption_name
        captions_vtt_response = requests.get(timedtext_api, params=request_captions)
        captions = webvtt_string_to_parsed(captions_vtt_response.text)
        return captions
