GraphQL API
===========

When running the backend, the API is accessible at the endpoint ``/graphql``. If you're new to GraphQL a good place to
start would be an interactive GraphQL explorer such as GraphiQL or Insomnia.

A typical API flow is to use the ``devices`` query to return a list of devices, then use the ``contacts`` or ``events``
queries to retrieve data, possibly refining it through filters. After a suitable filter has been found, the
``createSubset`` mutation can be used to create a new device or devices based on the filter.

Queries
-------

``devices`` : retrieve a list of devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. graphiql ::
    :query:
        {
            devices {
                id
                country_code
                is_subset
            }
        }
    :response:
        {
            "data": {
                "devices": [
                    {
                        "id": "example_device",
                        "country_code": "GB",
                        "is_subset": false,
                    },
                    {
                        "id": "example_device_subset",
                        "country_code": "GB",
                        "is_subset": true,
                    }
                ]
            }
        }

The returned value is a list of Devices containing the following fields:

* ``id``: A unique identifier for the device, used in other queries and mutations to select devices of interest.
  Currently corresponds to the name of the directory containing the device dump, but this may change in future.
* ``country_code``: the ISO 3166-1 alpha-2 country code of the device, used when canonicalising local phone numbers found on the device.
* ``is_subset``: indicates whether this device was subsetted from another device -- in the example GUI, only subsetted devices can be deleted.


``contacts(deviceIds, filter)`` : retrieve a list of contacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve a list of Contacts and, optionally, identify matching contacts across devices and providers.

.. graphiql ::
   :query:
    {
        contacts(deviceIds: ["example_device"]) {
            contacts {
                id
                name {
                    first
                    last
                    display
                }
                phone
                email
            }
            mergedContacts {
                id
                name {
                    first
                    last
                    display
                }
                phone
                email
                mergedIds
            }
        }
    }
   :response:
    {
        "data": {
            "contacts": {
                "contacts": [
                    {
                        "id": "example_device:android-com.whatsapp.android:4400000000001@s.whatsapp.net",
                        "name": {
                            "first": null,
                            "last": null,
                            "display": "Nicholas"
                        },
                        "phone": "+440000000001",
                        "email": null
                    },
                    {
                        "id": "example_device:android-com.whatsapp.android:4400000000002@s.whatsapp.net",
                        "name": {
                            "first": "Giles",
                            "last": "Murchison",
                            "display": "Giles Murchison"
                        },
                        "phone": "+440000000002",
                        "email": null
                    },
                    {
                        "id": "example_device:android-com.android.providers.telephony:16",
                        "name": {
                            "first": null,
                            "last": null,
                            "display": "+4400000000002"
                        },
                        "phone": "+440000000002",
                        "email": null
                    },
                    {
                        "id": "example_device:android-com.android.providers.telephony:3",
                        "name": {
                            "first": null,
                            "last": null,
                            "display": "00000000001"
                        },
                        "phone": "00000000001",
                        "email": null
                    },
                    {
                        "id": "example_device:android-com.android.providers.contacts:2",
                        "name": {
                            "first": null,
                            "last": null,
                            "display": "Nicholas"
                        },
                        "phone": "+44 00000 000001",
                        "email": null
                    }
                ],
                "mergedContacts": [
                    {
                        "id": "merged:merged:f825921ef6b9668f16a44ceac25773a6755c48e15857386b83a2638044173d25",
                        "name": {
                            "first": null,
                            "last": null,
                            "display": "Nicholas"
                        },
                        "phone": "+4400000000001",
                        "mergedIds": [
                            "example_device:android-com.whatsapp.android:440000000001@s.whatsapp.net",
                            "example_device:android-com.android.providers.telephony:3",
                            "example_device:android-com.android.providers.contacts:2"
                        ]
                    },
                    {
                        "id": "merged:merged:8c5215258319059cea52e2cf578a06c174ebac57a5bc01ac7f4bc5060ecc8be7",
                        "name": {
                            "first": "Giles",
                            "last": "Murchison",
                            "display": "Giles Murchison"
                        },
                        "phone": "+440000000002",
                        "mergedIds": [
                            "example_device:android-com.whatsapp.android:440000000002@s.whatsapp.net",
                            "example_device:android-com.android.providers.telephony:16"
                        ]
                    }
                ]
            }
        }
    }

}

Parameters:

* ``deviceIds``: a list of device IDs to retrieve contacts from. The list is required and an empty list will return no contacts.
* ``filter``: a filter to apply to the contacts. Filter is optional; if not provided, all contacts will be returned.

The returned value is a ContactsResult type containing a list of Contacts and MergedContacts. Contacts are merged based
on their canonical phone number, which is in `E164 format <https://en.wikipedia.org/wiki/E.164>`_ -- a plus sign, a
country code, and the number, with no spaces. The merged contact's personal information fields (name and email) are
chosen, somewhat arbitrarily, from the contact with the longest amount of text in that field.

Merged contact results contain a ``mergedIds`` field which is a list of contact IDs which were merged to produce the
result.

Other fields include:

* ``id``: a unique identifier for the contact, which may be used for filtering. Note that MergedContact IDs should not
  be used: if you wish to filter on a merged contact, supply the IDs of all constituent contacts (i.e. the ``mergedIds``
  list).
* ``name``: a Name object consisting of ``first`` (first name), ``last`` (last name), and ``display`` (display name).
  ``display`` is user-editable in some apps and may thus not be related to ``first`` and ``last``. Additionally, many
  Contact sources do not provide first and last names.
* ``phone``: the contact's phone number. Merged contacts supply this in E164 format, but regular Contacts may supply any 
  data here -- an invalid number, random text, or nothing at all.
* ``email``: the contact's email address. Like phone numbers, there are absolutely no guarantees about the format or
  validity of this field.

``events(deviceIds, filter)`` : retrieve a list of events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. graphiql ::
  :query:
    {
        events(deviceIds: ["example_device"]) {
                __typename
                deviceId
                events {
                providerName
                timestamp
                ... on MessageEvent {
                    id
                    session {
                        sessionId
                        name
                        participants {
                            id
                            name {
                                display
                            }
                            phone
                        }
                    }
                    sessionId
                    sender {
                        id
                        name {
                            display
                        }
                        phone
                    }
                    text
                    fromMe
                }
                }
        }
    }
  :response:
    {
        "data": {
            "events": [
                {
                    "__typename": "EventsForDevice",
                    "deviceId": "example_device",
                    "events": [
                        {
                            "providerName": "android-com.android.providers.telephony",
                            "timestamp": "2022-11-08T13:51:59.124000",
                            "id": null,
                            "session": {
                                "sessionId": "3",
                                "name": "",
                                "participants": [
                                    {
                                        "id": "example_device:android-com.android.providers.telephony:3",
                                        "name": {
                                            "display": "00000000001"
                                        },
                                        "phone": "00000000001"
                                    }
                                ]
                            },
                            "sessionId": "3",
                            "sender": {
                                "id": "example_device:android-com.android.providers.telephony:3",
                                "name": {
                                    "display": "00000000001"
                                },
                                "phone": "00000000001"
                            },
                            "text": "My number",
                            "fromMe": true
                        },
                        {
                            "providerName": "android-com.whatsapp.android",
                            "timestamp": "2022-11-08T14:13:18",
                            "id": null,
                            "session": {
                                "sessionId": "2",
                                "name": null,
                                "participants": [
                                    {
                                        "id": "example_device:android-com.whatsapp.android:440000000001@s.whatsapp.net",
                                        "name": {
                                            "display": "Nicholas"
                                        },
                                        "phone": "+440000000001"
                                    }
                                ]
                            },
                            "sessionId": "2",
                            "sender": {
                                "id": "example_device:android-com.whatsapp.android:440000000001@s.whatsapp.net",
                                "name": {
                                    "display": "Nicholas"
                                },
                                "phone": "+440000000001"
                            },
                            "text": "Hello! I’m messaging in WhatsApp.",
                            "fromMe": false
                        },
                        {
                            "providerName": "android-com.whatsapp.android",
                            "timestamp": "2022-11-08T14:17:30.090000",
                            "id": null,
                            "session": null,
                            "sessionId": "2",
                            "sender": {
                                "id": "example_device:android-com.whatsapp.android:00000000003@s.whatsapp.net",
                                "name": {
                                    "display": null
                                },
                                "phone": "440000000003"
                            },
                            "text": "Oh hi!!",
                            "fromMe": true
                        }
                    ]
                }
            ]
        }
    }
