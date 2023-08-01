# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from abc import ABC, abstractmethod

from .media import MediaData


class Provider(ABC):
    NAME = None
    FRIENDLY_NAME = None  # for displaying to users

    PII_FIELDS = NotImplemented

    @classmethod
    @abstractmethod
    def from_filesystem(cls, fs):
        """
        Return a class instance if the provider recognises data on this filesystem, None if not.
        """
        return None

    @abstractmethod
    def subset(self, subsetter, events, contacts):
        """
        Create a subset using the given events and contacts.
        """
        return None

    @abstractmethod
    def search_events(self, device, filter_):
        """
        Search for events matching ``filter_``, which is an EventFilter.
        """
        return []

    @abstractmethod
    def search_contacts(self, filter_):
        """
        Return a list of Contacts matching ``filter_``.
        """

    @abstractmethod
    def get_media(self, local_id) -> MediaData:
        """
        return a MediaData object supplying the picture, video, sound, etc identified by 'local_id'.
        """


def find_providers(fs) -> dict[str, Provider]:
    """
    Return a list of providers that recognise data on this filesystem.
    """
    from . import providers

    providers = {}
    for provider in Provider.__subclasses__():
        instance = provider.from_filesystem(fs)
        if instance:
            providers[provider.NAME] = instance

    return providers
