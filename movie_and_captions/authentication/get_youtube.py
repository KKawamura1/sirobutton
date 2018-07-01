import apiclient.discovery
import os.path


def _read_api_key() -> str:
    api_key_path = os.path.join(os.path.dirname(__file__), 'API_KEY')
    with open(api_key_path, 'r') as f:
        api_key = f.read()
    return api_key


def build_youtube_service() -> apiclient.discovery.Resource:
    api_service_name = 'youtube'
    api_version = 'v3'
    api_key = _read_api_key()
    service = apiclient.discovery.build(api_service_name, api_version, developerKey=api_key,
                                        cache_discovery=False)
    return service
