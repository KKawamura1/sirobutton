from typing import NamedTuple
import datetime


class VideoInfo(NamedTuple):
    video_id: str
    title: str
    published: datetime.datetime
