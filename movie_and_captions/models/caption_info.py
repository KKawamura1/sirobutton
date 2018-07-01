from typing import NamedTuple
import datetime


class CaptionInfo(NamedTuple):
    caption_id: str
    name: str
    last_updated: datetime.datetime
    language: str
    track_kind: str
