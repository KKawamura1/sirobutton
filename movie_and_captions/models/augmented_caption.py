from typing import NamedTuple
from datetime import time


class AugmentedCaption(NamedTuple):
    begin: time
    end: time
    content: str
    short_title: str
    yomi: str
