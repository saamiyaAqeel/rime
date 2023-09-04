# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

"""
A provider which finds any media on the device not already found by other providers.
"""
from datetime import datetime
from dataclasses import dataclass

import filetype

from ..provider import Provider
from ..event import MediaEvent, GenericEventInfo
from ..media import MediaData

from . import providernames
from .providernames import ANDROID_GENERIC_MEDIA, ANDROID_GENERIC_MEDIA_FRIENDLY

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


@dataclass
class DirentryProviderInfo:
    provider_name: str
    is_user_content: bool


_DIRENTRY_TO_PROVIDER_PREFIXES = {
    '/sdcard/Android/data/com.hmdglobal.camera2/': DirentryProviderInfo(providernames.ANDROID_CAMERA2_HMDGLOBAL, False),
    '/sdcard/DCIM/Camera/': DirentryProviderInfo(providernames.ANDROID_CAMERA, True),
    '/sdcard/WhatsApp/Media/': DirentryProviderInfo(providernames.ANDROID_WHATSAPP, True),
    '/sdcard/com.whatsapp/files/': DirentryProviderInfo(providernames.ANDROID_WHATSAPP, False),
}


def _guess_provider_for_entity(category) -> DirentryProviderInfo | None:
    for prefix, info in _DIRENTRY_TO_PROVIDER_PREFIXES.items():
        if category.startswith(prefix):
            return info

    return None


class AndroidGenericMedia(Provider):
    NAME = ANDROID_GENERIC_MEDIA
    FRIENDLY_NAME = ANDROID_GENERIC_MEDIA_FRIENDLY

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
                category = _dirname(direntry.path)

                # Attempt to label the provider. We either label it as definitively coming from a
                # specific provider, or, if it's user or unknown content, we default to the
                # unknown contact.
                direntry_provider_info = _guess_provider_for_entity(category)
                if direntry_provider_info and not direntry_provider_info.is_user_content:
                    sender = device.provider_contact(direntry_provider_info.provider_name)
                    is_user_generated = False
                else:
                    sender = device.unknown_contact
                    is_user_generated = True

                generic_event_info = GenericEventInfo(
                    category=category,
                    is_user_generated=is_user_generated,
                )

                yield MediaEvent(
                    mime_type=metadata.mime,
                    local_id=direntry.path,
                    id_=direntry.path,
                    timestamp=datetime.fromtimestamp(direntry.stat().st_ctime),
                    generic_event_info=generic_event_info,
                    provider=self,
                    sender=sender,
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
        if self.fs.id_ not in _metadata_cache or local_id not in _metadata_cache[self.fs.id_]:
            _build_metadata_cache(self.fs)

        direntry, metadata = _metadata_cache[self.fs.id_][local_id]

        # TODO: let the filesystem cache DirEntry objects here?
        return MediaData(
            mime_type=metadata.mime,
            handle=self.fs.open(direntry.path),
            length=direntry.stat().st_size,
        )
