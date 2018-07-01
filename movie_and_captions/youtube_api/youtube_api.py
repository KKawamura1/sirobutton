from apiclient.http import HttpRequest, HttpError
from apiclient.discovery import Resource
from typing import Mapping, Sequence, List, Any
from logging import Logger, getLogger
import datetime
import sys

from movie_and_captions.models import CaptionInfo, VideoInfo


class YoutubeAPI:
    def __init__(
            self,
            resource: Resource,
            logger: Logger = getLogger(__name__)
    ) -> None:
        self._resource = resource
        self._logger = logger

    def _execute_with_repeat(
            self,
            request: HttpRequest,
            retry_num: int = 10
    ) -> Any:
        for i in range(retry_num):
            try:
                response = request.execute()
                break
            except HttpError:
                self._logger.warning('An http error occurs during execution, retrying...')
                self._logger.warning('Error information: {}'.format(sys.exc_info()))
        else:
            raise HttpError('http request failed after {} trying.'.format(retry_num))
        return response

    def _get_list_result_with_fields(
            self,
            collection: Resource,
            filters: Mapping[str, str],
            field_selectors: Sequence[str]
    ) -> List[str]:
        assert field_selectors
        part = field_selectors[0]
        results = []
        request = collection.list(part=part, **filters)
        while request is not None:
            response = self._execute_with_repeat(request)
            for item in response['items']:
                tmp = item
                for field_selector in field_selectors:
                    tmp = tmp[field_selector]
                results.append(tmp)
            request = collection.list_next(request, response)
        return results

    def get_playlist_id_from_channel_id(
            self,
            target_channel_id: str
    ) -> str:
        collection = self._resource.channels()
        filters = dict(id=target_channel_id)
        field_selectors = ['contentDetails', 'relatedPlaylists', 'uploads']

        return self._get_list_result_with_fields(collection, filters, field_selectors)[0]

    def get_video_ids_from_playlist_id(
            self,
            target_playlist_id: str
    ) -> List[str]:
        collection = self._resource.playlistItems()
        max_results_max = '50'
        filters = dict(playlistId=target_playlist_id, maxResults=max_results_max)
        field_selectors = ['contentDetails', 'videoId']

        return self._get_list_result_with_fields(collection, filters, field_selectors)

    def get_video_info_from_video_id(
            self,
            target_video_id: str
    ) -> VideoInfo:
        collection = self._resource.videos()
        filters = dict(id=target_video_id)
        parts = ['snippet']
        part = ','.join(parts)
        fields = 'items(snippet(title,publishedAt))'
        request = collection.list(part=part, fields=fields, **filters)
        response = self._execute_with_repeat(request)['items'][0]
        title = response['snippet']['title']
        published = self._iso_8601_string_to_time(response['snippet']['publishedAt'])
        video_info = VideoInfo(target_video_id, title, published)
        return video_info

    def get_caption_infos_from_video_id(
            self,
            target_video_id: str,
    ) -> List[CaptionInfo]:
        # caution: this method takes more amount of `quota` than other APIs!
        collection = self._resource.captions()
        filters = dict(videoId=target_video_id)
        parts = ['id', 'snippet']
        part = ','.join(parts)
        fields = 'items(id,snippet(name,lastUpdated,language,trackKind))'
        request = collection.list(part=part, fields=fields, **filters)
        response = self._execute_with_repeat(request)
        caption_infos = [
            CaptionInfo(item['id'], item['snippet']['name'],
                        self._iso_8601_string_to_time(item['snippet']['lastUpdated']),
                        item['snippet']['language'], item['snippet']['trackKind'])
            for item in response['items']
        ]
        return caption_infos

    def _iso_8601_string_to_time(
            self,
            string: str
    ) -> datetime.datetime:
        accepts_format = 'YYYY-MM-DDThh:mm:ss'
        time_format = '%Y-%m-%dT%H:%M:%S'

        assert len(string) >= len(accepts_format)
        string = string[:len(accepts_format)]
        time_wo_tz = datetime.datetime.strptime(string, time_format)
        return datetime.datetime.combine(time_wo_tz.date(), time_wo_tz.time(),
                                         datetime.timezone.utc)
