import django.db
from logging import Logger, getLogger
from typing import Union, Mapping, Any, Callable, Tuple, AbstractSet
from pathlib import Path
import pickle
from tqdm import tqdm

from hello.models import Video, CaptionTrack, Subtitle
from add_captions_to_database.data import Data


class AddCaptionsToDatabase:
    def __init__(self, logger: Logger = getLogger(__name__)) -> None:
        self._logger = logger

    def do(
            self,
            input_data: Data
    ) -> None:
        video_assigns = dict(video_id='video_id', title='title', published='published')
        caption_track_assigns = dict(caption_id='caption_id', language='language',
                                     parent_video='video')
        subtitle_assigns = dict(begin='begin', end='end', content='content',
                                short_title='short_title', yomi='yomi',
                                parent_caption_track='captiontrack')
        video_identities = set(['video_id'])
        caption_track_identities = set(['caption_id'])
        subtitle_identities = set(['content'])

        for video_datum in tqdm(input_data):
            # video
            video_info = video_datum['video_info']
            video_item = self._create_or_update_if_necessary(Video, video_info,
                                                             video_identities, video_assigns)
            # caption track
            caption_info = video_datum['caption_info']
            caption_info['parent_video'] = video_item
            caption_track_item = self._create_or_update_if_necessary(CaptionTrack, caption_info,
                                                                     caption_track_identities,
                                                                     caption_track_assigns)
            # subtitle (a.k.a. caption)
            captions = video_datum['augmented_captions']
            for caption in captions:
                caption['parent_caption_track'] = caption_track_item
                self._create_or_update_if_necessary(Subtitle, caption,
                                                    subtitle_identities,
                                                    subtitle_assigns)

    def _create_or_update_if_necessary(
            self,
            model: django.db.models.Model,
            data_dict: Mapping[str, Any],
            require_keys: AbstractSet[str],
            data_to_object_assignment: Mapping[str, str],
    ) -> Any:
        """call get_or_create_func, update the item if necessary, and return it"""

        defaults = {val: data_dict[key] for key, val in data_to_object_assignment.items()}
        identities = {data_to_object_assignment[key]: data_dict[key] for key in require_keys}
        item, newly_created = model.objects.get_or_create(defaults=defaults, **identities)
        if not newly_created:
            updated = False
            # check the necessity for update
            for key, val in defaults.items():
                if getattr(item, key, None) != val:
                    setattr(item, key, val)
                    updated = True
            if updated:
                # do update
                item.save()
                self._logger.debug('item {} updated'.format(item))
            else:
                self._logger.debug('item {} is not updated since not required'.format(item))
        else:
            self._logger.debug('item {} is not created since it exists'.format(item))
        return item
