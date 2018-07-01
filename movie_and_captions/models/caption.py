from typing import NamedTuple
from datetime import time


class Caption(NamedTuple):
    begin: time
    end: time
    content: str
