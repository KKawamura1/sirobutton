import webvtt
from typing import List
import datetime
import re
from movie_and_captions.models import Caption, CaptionInfo, VideoInfo


TIMESTAMP_PATTERN = re.compile('^(\d+)?:?(\d{2}):(\d{2})[.,](\d{3})$')


def _webvtt_string_to_parsed_original_structure(webvtt_string: str) -> List[webvtt.Caption]:
    parser = webvtt.parsers.WebVTTParser()
    lines = webvtt_string.split('\n')
    parser._validate(lines)
    parser._parse(lines)
    return parser.captions


def _timestamp_to_time(timestamp: str) -> datetime.time:
    m = TIMESTAMP_PATTERN.match(timestamp)
    assert m is not None
    hours, minutes, seconds, milisecs = m.groups()
    if hours is None:
        hours = '0'
    assert all([elem is not None for elem in [minutes, seconds, milisecs]])
    return datetime.time(int(hours), int(minutes), int(seconds), int(milisecs) * 1000)


def _original_caption_to_my_caption(
        original_caption: webvtt.Caption
) -> Caption:
    return Caption(_timestamp_to_time(original_caption.start),
                   _timestamp_to_time(original_caption.end),
                   original_caption.text)


def webvtt_string_to_parsed(
        webvtt_string: str
) -> List[Caption]:
    original_captions = _webvtt_string_to_parsed_original_structure(webvtt_string)
    return [_original_caption_to_my_caption(original_caption)
            for original_caption in original_captions]
