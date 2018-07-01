from typing import List, Dict, Any, Dict, Union


# Data: List[VideoDatum]
# VideoDatum: Dict[Key, Info]
# Key: OneOfThe['caption_info', 'video_info', 'captions']
# Info: Dict[str, Any] or List[Dict[str, Any]]

_Info = Union[Dict[str, Any], List[Dict[str, Any]]]
VideoDatum = Dict[str, _Info]

Data = List[VideoDatum]
