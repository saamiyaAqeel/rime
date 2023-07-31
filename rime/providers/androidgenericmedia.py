# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

"""
A provider which finds any media on the device not already found by other providers.
"""
from datetime import datetime

import filetype

from .provider import Provider
from ..event import MediaEvent
from ..media import MediaData

_metadata_cache = {}  # fs.id_: {path: (DirEntry, filetype.types.base.Type)}


# Chosen by fair dice roll.
# Just kidding, chosen by reference to https://github.com/h2non/filetype.py
FILE_HEADER_GUESS_LENGTH = 261


def _walk(fs, path):
    for entry in fs.scandir(path):
        if entry.is_dir():
            yield from _walk(fs, entry.path)
        else:
            yield entry


def _build_metadata_cache(fs):
    global _metadata_cache

    _metadata_cache[fs.id_] = {}
    if fs.exists('/sdcard'):
        for direntry in _walk(fs, '/sdcard'):
            with fs.open(direntry.path) as f:
                first_bytes = f.read(FILE_HEADER_GUESS_LENGTH)
            if first_bytes:
                _metadata_cache[fs.id_][direntry.path] = (direntry, filetype.guess(first_bytes))


def _dirname(filename):
    """
    Return the directory containing 'filename', which is assumed to be a file.

    Not using os.path because there's no guarantee that the OS we're on behaves like Android.
    """
    if '/' not in filename:
        return '/'

    return filename[:filename.rindex('/')]


class AndroidGenericMedia(Provider):
    NAME = 'android-generic-media'
    FRIENDLY_NAME = 'Android Generic Media'

    PII_FIELDS = []

    def __init__(self, fs):
        self.fs = fs

    @classmethod
    def from_filesystem(cls, fs):
        return cls(fs)

    def subset(self, subsetter, events, contacts):
        """
        Create a subset using the given events and contacts.
        """
        return None

    def search_events(self, device, filter_):
        """
        Search for events matching ``filter_``, which is an EventFilter.
        """
        if self.fs.id_ not in _metadata_cache:
            _build_metadata_cache(self.fs)

        for direntry, metadata in _metadata_cache[self.fs.id_].values():
            if metadata is None:
                continue

            if metadata.mime.startswith('image/') or metadata.mime.startswith('video/'):
                yield MediaEvent(
                    mime_type=metadata.mime,
                    local_id=direntry.path,
                    id_=direntry.path,
                    timestamp=datetime.fromtimestamp(direntry.stat().st_ctime),
                    source=_dirname(direntry.path),
                    provider=self
                )

    def search_contacts(self, filter_):
        """
        Return a list of Contacts matching ``filter_``.
        """
        return []

    def get_media(self, local_id) -> MediaData:
        """
        return a MediaData object supplying the picture, video, sound, etc identified by 'local_id'.
        """
        if local_id not in _metadata_cache[self.fs.id_]:
            _build_metadata_cache(self.fs)

        direntry, metadata = _metadata_cache[self.fs.id_][local_id]

        # TODO: let the filesystem cache DirEntry objects here?
        return MediaData(
            mime_type=metadata.mime,
            handle=self.fs.open(direntry.path),
            length=direntry.stat().st_size,
        )
