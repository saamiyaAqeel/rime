# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from re import Pattern
from datetime import datetime
from dataclasses import dataclass

from .event import MessageEvent
from .contact import GlobalContactId


class _AlwaysMatchesPattern:
    def search(self, input):
        return True

    def match(self, input):
        return True


TheAlwaysMatchesPattern = _AlwaysMatchesPattern()


@dataclass
class ProvidersFilter:
    name_regex: Pattern | _AlwaysMatchesPattern

    @classmethod
    def empty(cls):
        return cls(name_regex=TheAlwaysMatchesPattern)


@dataclass(frozen=True)
class EventsFilter:
    participant_ids: list[GlobalContactId] | None = None
    timestamp_start: datetime | None = None
    timestamp_end: datetime | None = None
    type_names: set[str] | None = None
    provider_names: set[str] | None = None
    generic_event_category_regex: Pattern | _AlwaysMatchesPattern = TheAlwaysMatchesPattern

    def accepts_type(self, type_name):
        return self.type_names is None or type_name in self.type_names

    @classmethod
    def empty(cls):
        return cls()

    def apply(self, events):
        return list(filter(self.matches, events))

    def matches(self, event):
        assert event.id_

        if self.provider_names is not None and event.provider.NAME not in self.provider_names:
            return False

        if not self.accepts_type(event.__class__.__name__):
            return False

        if self.participant_ids:
            # Create global contact IDs for comparison and include group chat participants.

            event_participants = set([GlobalContactId.from_contact(event.sender)])

            if isinstance(event, MessageEvent) and event.session:
                event_participants.update([GlobalContactId.from_contact(p) for p in event.session.participants])

            if not event_participants.intersection(set(self.participant_ids)):
                return False

        assert isinstance(event.timestamp, datetime)

        if self.timestamp_start and event.timestamp < self.timestamp_start:
            return False

        if self.timestamp_end and event.timestamp > self.timestamp_end:
            return False

        if event.generic_event_info:
            if not self.generic_event_category_regex.search(event.generic_event_info.category or ''):
                return False

        return True


@dataclass
class ContactsFilter:
    name_regex: Pattern | _AlwaysMatchesPattern

    @classmethod
    def empty(cls):
        return cls(TheAlwaysMatchesPattern)

    def is_empty(self):
        return not self.name_regex

    def apply(self, contacts):
        # TODO
        return contacts
