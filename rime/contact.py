# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from dataclasses import dataclass
from typing import Any


@dataclass
class Name:
    first: str | None = None
    last: str | None = None
    display: str | None = None

    def full_name(self):
        if self.display:
            return self.display
        elif self.first and self.last:
            return f"{self.first} {self.last}"
        elif self.first:
            return self.first
        elif self.last:
            return self.last

        return ''


# TODO: a Contact may have more than one phone or email
@dataclass
class Contact:
    local_id: str  # Unique to the provider only. The GraphQL layer combines this with providerName for the UI.
    device_id: str
    name: Name | None = None
    providerName: str | None = None
    providerFriendlyName: str | None = None
    phone: str | None = None
    email: str | None = None
    # Provider-specific data to allow the contact to be recreated during subsetting:
    provider_data: Any = None

    def __setattr__(self, key, value):
        """
        Helper to let you set name.field directly.
        """
        if '.' in key:
            assert key.count('.') == 1
            key, subkey = key.split('.')
            setattr(getattr(self, key), subkey, value)
        else:
            super().__setattr__(key, value)

    def __hash__(self):
        return hash((self.device_id, self.local_id))


@dataclass(frozen=True)
class GlobalContactId:
    """
    Uniquely identifies a contact.

    Normally providers shouldn't need to worry about GlobalContactId as it's mostly for the GUI
    and thus handled by the GraphQL layer.
    """
    device_id: str
    provider_name: str
    local_id: str

    @classmethod
    def from_string(cls, s):
        device_id, provider_name, local_id = s.split(':', 2)
        return cls(device_id=device_id, provider_name=provider_name, local_id=local_id)

    @classmethod
    def from_contact(cls, contact):
        return cls(device_id=contact.device_id, provider_name=contact.providerName, local_id=contact.local_id)

    @staticmethod
    def make_global_id_str(contact):
        return f"{contact.device_id}:{contact.providerName}:{contact.local_id}"
