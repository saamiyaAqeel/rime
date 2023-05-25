# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from abc import ABC, abstractmethod

class LazyContactProvider(ABC):
    @abstractmethod
    def contact_load_all(self):
        """
        Return an iterator returning dicts to be passed to contact_create().
        """
        raise NotImplementedError()

    @abstractmethod
    def contact_create(self, **kwargs):
        """
        Given a set of properties, return a Contact instance.
        """
        raise NotImplementedError()

    @abstractmethod
    def contact_unknown(self, local_id):
        """
        Contact was not present, so return kwargs for a new contact with the specified local_id return it.

        Return None if the contact could not be created (will raise KeyError in LazyContactProviderContacts)
        """
        raise NotImplementedError()

class LazyContactProviderContacts(dict):
    """
    """
    def __init__(self, provider: LazyContactProvider):
        super().__init__()
        self._loaded = False
        self.provider = provider

    def _load(self):
        if not self._loaded:
            for kwargs in self.provider.contact_load_all():
                obj = self.provider.contact_create(**kwargs)
                super().__setitem__(obj.local_id, obj)
            self._loaded = True

    def __getitem__(self, key):
        key = str(key)

        self._load()
        try:
            return super().__getitem__(key)
        except KeyError:
            kwargs = self.provider.contact_unknown(key)
            if kwargs is None:
                raise KeyError(key)
            obj = self.provider.contact_create(**kwargs)
            self[obj.local_id] = obj
            return obj

    def __setitem__(self, key, value):
        self._load()
        return super().__setitem__(str(key), value)

    def __contains__(self, key):
        self._load()
        return super().__contains__(str(key))

    def __iter__(self):
        self._load()
        return super().__iter__()

    def __len__(self):
        self._load()
        return super().__len__()

    def keys(self):
        self._load()
        return super().keys()

    def values(self):
        self._load()
        return super().values()
