# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

"""
An Event is something that occurs at a particular time in the dataset
of a Provider.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .contact import Contact
from .provider import Provider


@dataclass
class GenericEventInfo:
    category: str


@dataclass
class Event:
    id_: str
    timestamp: datetime
    provider: Provider
    generic_event_info: GenericEventInfo | None = None  # see the various *generic*.py providers
    device_id: str | None = None  # Added by graphql layer, no need to set in Provider
    provider_data: Any = None


@dataclass(kw_only=True)
class MessageSession:
    local_id: str
    provider: Provider
    name: str
    participants: tuple[Contact]
    provider_data: Any = None
    global_id: str | None = None  # Added by graphql layer, no need to set in Provider

    def __hash__(self):
        key = f'{self.local_id}:{self.provider.NAME}'
        return hash(key)


@dataclass(kw_only=True)
class Media:
    """
    Represents either standalone media or media associated with a MessageEvent.
    """
    mime_type: str
    local_id: str  # A provider-specific reference to the media.


@dataclass(kw_only=True)
class MessageEvent(Event):
    session_id: str
    text: str
    sender: Contact | None = None
    from_me: bool = False
    session: MessageSession | None = None
    media: Media | None = None


@dataclass(kw_only=True)
class MediaEvent(Media, Event):
    # Nothing required.
    pass
