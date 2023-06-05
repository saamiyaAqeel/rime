# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE. :)
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd
import hashlib
from dataclasses import dataclass

import phonenumbers

from .contact import Contact, Name


@dataclass
class MergedContact:
    # local_id: Unique to the provider only. The GraphQL layer combines this with device ID and providerName for the UI.
    local_id: str
    contacts: list[Contact]
    name: Name | None = None
    phone: str | None = None
    email: str | None = None


def _hash_contact_ids(contacts) -> str:
    hasher = hashlib.sha256()
    for contact in contacts:
        hasher.update(str(contact.local_id).encode('utf-8'))
        hasher.update(contact.device_id.encode('utf-8'))
        hasher.update(contact.providerName.encode('utf-8'))

    return hasher.hexdigest()


def merge_contacts(rime, contacts: list[Contact]) -> list[MergedContact]:
    """
    Create a list of merged contacts by comparing phone numbers using the phonenumbers library.

    Every contact in the input list will be accounted for, such that the list of all merged_contact.contact
    lists will be equal to the input list apart from ordering.
    """
    # Find contacts having the same phone number.
    unmergeable_contacts = []  # list of MergedContact
    similar_contacts = {}  # phone number in E164 format to list of Contact objects
    for contact in contacts:
        try:
            number = phonenumbers.parse(contact.phone, rime.device_for_id(contact.device_id).country_code)
            number_str = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            number_str = None

        if number_str is not None:
            # We could get a canonical phone number, so merging is possible.
            if number_str not in similar_contacts:
                similar_contacts[number_str] = []

            similar_contacts[number_str].append(contact)
        else:
            # We couldn't canonicalise the phone number, so create a unique "merged" contact.
            unmergeable_contacts.append(MergedContact(
                local_id=_hash_contact_ids([contact]),
                contacts=[contact],
                name=contact.name,
                phone=contact.phone,
                email=contact.email,))

    # Use the above to create MergedContact objects.
    merged_contacts = []
    for number_str, similar_contacts in similar_contacts.items():
        assert similar_contacts

        local_id = _hash_contact_ids(similar_contacts)

        # Take the longest full name available as the contact's name.
        contact_names = [contact.name for contact in similar_contacts if contact.name]
        contact_names.sort(key=lambda name: len(name.full_name()) if name else 0, reverse=True)
        name = contact_names[0] if contact_names else None

        # Take the longest email available as the contact's email.
        contact_emails = [contact.email for contact in similar_contacts if contact.email]
        contact_emails.sort(key=lambda email: len(email) if email else 0, reverse=True)
        email = contact_emails[0] if contact_emails else None

        merged_contacts.append(MergedContact(
            local_id=local_id,
            contacts=similar_contacts,
            name=name,
            phone=number_str,
            email=email,))

    merged_contacts.extend(unmergeable_contacts)

    return merged_contacts
