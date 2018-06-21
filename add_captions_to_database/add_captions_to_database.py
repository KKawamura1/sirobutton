import django.db
from logging import Logger, getLogger
from typing import Union, Mapping, Any, Callable, Tuple, AbstractSet
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
        video_assigns = dict(video_id='video_id', title='title')
        caption_track_assigns = dict(caption_id='caption_id', language='language',
                                     parent_video='video')
        subtitle_assigns = dict(begin='begin', end='end', content='content',
                                short_title='short_title', yomi='yomi',
                                parent_caption_track='captiontrack')
        video_identities = set(['video_id'])
        caption_track_identities = set(['caption_id'])
        subtitle_identities = set(['content'])

        input_dir = Path(input_dir).resolve()
        assert input_dir.is_dir()
        for caption_path in input_dir.glob('**/augmented_captions.pkl'):
            caption_info_path = caption_path.parent / 'caption_info.pkl'
            video_info_path = caption_path.parent / 'video_info.pkl'
            assert all([path.is_file()
                        for path in [caption_path, caption_info_path, video_info_path]])
            # video
            with video_info_path.open('rb') as f:
                video_info = pickle.load(f)
            video_item = self._create_or_update_if_necessary(Video, video_info,
                                                             video_identities, video_assigns)
            # caption track
            with caption_info_path.open('rb') as f:
                caption_info = pickle.load(f)
            caption_info['parent_video'] = video_item
            caption_track_item = self._create_or_update_if_necessary(CaptionTrack, caption_info,
                                                                     caption_track_identities,
                                                                     caption_track_assigns)
            # subtitle (a.k.a. caption)
            with caption_path.open('rb') as f:
                captions = pickle.load(f)
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
