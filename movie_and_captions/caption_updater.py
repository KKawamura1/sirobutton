import datetime
from logging import getLogger, Logger
from typing import Sequence, Optional, Union, Optional
from pathlib import Path
from tqdm import tqdm
import pickle

from movie_and_captions.youtube_api import YoutubeAPI, DirtyYoutubeAPI
from movie_and_captions.models import CaptionInfo
from movie_and_captions.data import Data, VideoDatum


class CaptionUpdater:
    def __init__(
            self,
            youtube_api: YoutubeAPI,
            dirty_youtube_api: DirtyYoutubeAPI = None,
            logger: Logger = getLogger(__name__)
    ) -> None:
        self._youtube_api = youtube_api
        self._logger = logger
        self._dirty_youtube_api = dirty_youtube_api

    def _check_caption(
            self,
            caption_info: CaptionInfo,
            last_updated: datetime.datetime
    ) -> bool:
        # last update time check
        if caption_info.last_updated <= last_updated:
            self._logger.debug('Last update for this caption is {} <= memorized last update is {}'
                               .format(caption_info.last_updated, last_updated))
            return False
        # language check
        if caption_info.language[:2] != 'ja':
            self._logger.debug('caption is written in {}, not {}'
                               .format(caption_info.language, 'ja'))
            return False
        # auto generated check
        if caption_info.track_kind == 'ASR':
            self._logger.debug('caption is automatically generated')
            return False
        self._logger.info('caption {} is matched.'.format(caption_info))
        return True

    def _get_valid_caption(
            self,
            caption_infos: Sequence[CaptionInfo],
            last_updated: datetime.datetime
    ) -> Optional[CaptionInfo]:
        valid_caption_infos = [info for info in caption_infos
                               if self._check_caption(info, last_updated)]
        if len(valid_caption_infos) == 0:
            return None
        else:
            assert len(valid_caption_infos) == 1
            return valid_caption_infos[0]

    def do(
            self,
            target_channel_id: str,
            old_data: Data
    ) -> Data:
        playlist_id = self._youtube_api.get_playlist_id_from_channel_id(target_channel_id)
        video_ids = self._youtube_api.get_video_ids_from_playlist_id(playlist_id)

        video_id_to_data = {old_datum['video_info']['video_id']: old_datum  # type: ignore
                            for old_datum in old_data}

        new_data: Data = []
        for video_id in tqdm(video_ids):
            # find if the specified video exists in the old_data
            old_datum: Optional[VideoDatum]
            if video_id in video_id_to_data:
                old_datum = video_id_to_data[video_id]
                old_caption_info = CaptionInfo(**old_datum['caption_info'])  # type: ignore
                last_updated = old_caption_info.last_updated
            else:
                old_datum = None
                last_updated = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
            caption_infos = self._youtube_api.get_caption_infos_from_video_id(video_id)
            caption_info = self._get_valid_caption(caption_infos, last_updated)
            if caption_info is not None:
                self._logger.debug('valid caption is found. downloading.')
                video_info = self._youtube_api.get_video_info_from_video_id(video_id)
                assert self._dirty_youtube_api is not None
                captions = self._dirty_youtube_api.download_caption(video_info, caption_info)

                # convert into dicts
                caption_info_asdict = caption_info._asdict()
                video_info_asdict = video_info._asdict()
                captions_asdicts = [caption._asdict() for caption in captions]

                # add new captions
                new_data.append(dict(
                    captions=captions_asdicts,
                    caption_info=caption_info_asdict,
                    video_info=video_info_asdict
                ))
            else:
                if old_datum is not None:
                    new_data.append(old_datum)
        return new_data
