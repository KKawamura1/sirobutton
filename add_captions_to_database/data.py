from typing import List, Dict, Any, Dict, Union


# Data: List[VideoDatum]
# VideoDatum: Dict[Key, Info]
# Key: OneOfThe['caption_info', 'video_info', 'augmented_captions', 'captions']
# Info: Dict[str, Any] or List[Dict[str, Any]]

_Info = Union[Dict[str, Any], List[Dict[str, Any]]]
_VideoDatum = Dict[str, _Info]

Data = List[_VideoDatum]
