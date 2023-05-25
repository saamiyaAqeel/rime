import typing
from dataclasses import dataclass

@dataclass
class MediaData:
    mime_type: str
    # file-like object representing the media
    handle: typing.BinaryIO
    length: int
