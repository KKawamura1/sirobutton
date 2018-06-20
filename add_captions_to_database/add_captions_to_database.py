from logging import Logger, getLogger
from typing import Union
from pathlib import Path
import pickle
from hello.models import Video, CaptionTrack, Subtitle


class AddCaptionsToDatabase:
    def __init__(self, logger: Logger = getLogger(__name__)) -> None:
        self._logger = logger

    def do(
            self,
            input_dir: Union[Path, str]
    ) -> None:
        input_dir = Path(input_dir).resolve()
        assert input_dir.is_dir()
        for caption_path in input_dir.glob('**/augmented_captions.pkl'):
            caption_info_path = caption_path.parent / 'caption_info.pkl'
            video_info_path = caption_path.parent / 'video_info.pkl'
            assert all([path.is_file()
                        for path in [caption_path, caption_info_path, video_info_path]])
