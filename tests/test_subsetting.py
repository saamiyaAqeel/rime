import datetime
import os
import pprint

import gql
from gql.transport.aiohttp import AIOHTTPTransport

TEST_DEVICE_NAMES = os.environ.get('RIME_TEST_DEVICE_NAMES', 'android;iphone-6;iphone-8').split(';')
GQL_ENDPOINT = os.environ.get('RIME_GQL_ENDPOINT', 'http://localhost:8080/graphql')

client = gql.Client(transport=AIOHTTPTransport(url=GQL_ENDPOINT))

filter_events = gql.gql("""
  query getEvents($deviceIds: [String]!, $filter: EventsFilter) {
      events(deviceIds: $deviceIds, filter: $filter) {
        deviceId,
        events {
          id
          __typename
          providerName
          providerFriendlyName
          timestamp
          ... on MessageEvent {
              deviceId
              text
              fromMe
              sessionId
              session {
                name
                participants {
                    id name { first last display } phone email
                }
              }
              sender {
                  id
                  name { first last display }
                  phone
              }
          }
        }
      }
  }
""")

filter_contacts = gql.gql("""
	query getContacts($deviceIds: [String]!, $filter: ContactsFilter) {
		contacts(deviceIds: $deviceIds, filter: $filter) {
            contacts {
				id
				deviceId
				providerName
				providerFriendlyName
				name{first last display}
				email
				phone
			}
			mergedContacts {
				id
				name{first last display}
				phone
				mergedIds
			}
		}
	}
""")

create_subset = gql.gql("""
    mutation createSubset($target: DeviceIdPair!, $eventsFilter: EventsFilter, $contactsFilter: ContactsFilter) {
      createSubset(target: $target, eventsFilter: $eventsFilter, contactsFilter: $contactsFilter) {
         success
         deviceId
         errorMessage
         errorCode
      }
    }
""")

delete_device = gql.gql("""
	mutation deleteDevice($deviceId: String!) {
		deleteDevice(deviceId: $deviceId)
	}
""")

def call(query, **kw):
    return client.execute(query, variable_values=kw)

def _looks_like_global_contact_id(contact_id):
    return isinstance(contact_id, str) and contact_id.count(':') == 2

def _normalise_contact_id(contact_id):
    assert _looks_like_global_contact_id(contact_id), 'Contact ID does not look like a global ID'
    device_id, provider_name, local_id = contact_id.split(':')
    return f'_normalised_:{provider_name}:{local_id}'

class CompareFailed(Exception):
    def __init__(self, message, context):
        super().__init__(message)
        self.context = context

    def __str__(self):
        return f'{self.args[0]} (context: {"->".join(str(elem) for elem in self.context)})'

def _compare_event_ignoring_device_ids(event_a, event_b, context=None):
    assert type(event_a) == type(event_b), f'Classes do not match: {type(event_a)} != {type(event_b)}'

    if context is None:
        context = tuple()

    if isinstance(event_a, dict):
        for key in event_a.keys():
            if key == 'deviceId':
                continue
            elif key == 'id' and _looks_like_global_contact_id(event_a[key]):
                _compare_event_ignoring_device_ids(_normalise_contact_id(event_a[key]), _normalise_contact_id(event_b[key]),
                    context=context + (key,))
            else:
                _compare_event_ignoring_device_ids(event_a[key], event_b[key], context=context + (key,))
    elif isinstance(event_a, list):
        if context == ('session', 'participants'):
            # Order is irrelevant for session participants
            event_a = sorted(event_a, key=lambda x: x['id'])
            event_b = sorted(event_b, key=lambda x: x['id'])

        if len(event_a) != len(event_b):
            raise CompareFailed(f'List lengths do not match: {len(event_a)} != {len(event_b)}', context=context)

        for idx, (item_a, item_b) in enumerate(zip(event_a, event_b)):
            _compare_event_ignoring_device_ids(item_a, item_b, context=context + (idx,))
    elif event_a != event_b:
        raise CompareFailed(f'Values do not match: {event_a} != {event_b}', context=context)

def _compare_events_ignoring_device_ids(events_a, events_b):
    for event_a, event_b in zip(events_a, events_b):
        assert event_a['__typename'] == event_b['__typename'], 'Event type names do not match'
        try:
            _compare_event_ignoring_device_ids(event_a, event_b)
        except CompareFailed as e:
            print("Comparison failed while comparing events. Event A:")
            pprint.pprint(event_a)
            print("Event B:")
            pprint.pprint(event_b)
            raise

def test_maximal_filter():
    """
    An empty filter is equivalent to a maximally-broad filter.
    """
    for device_name in TEST_DEVICE_NAMES:
        all_events = call(filter_events, deviceIds=[device_name], filter=None)
        type_names = set()
        participant_ids = set()
        earliest_timestamp = datetime.datetime(1900, 1, 1)
        latest_timestamp = datetime.datetime(9999, 1, 1)

        for events_for_device in all_events['events']:
            for event in events_for_device['events']:
                type_names.add(event['__typename'])
                if event['__typename'] == 'MessageEvent':
                    if event['session'] is not None:
                        for contact in event['session']['participants']:
                            participant_ids.add(contact['id'])
                    if event['sender'] is not None:
                        participant_ids.add(event['sender']['id'])

                timestamp = datetime.datetime.fromisoformat(event['timestamp'])
                if earliest_timestamp is None or timestamp < earliest_timestamp:
                    earliest_timestamp = timestamp
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp

        events_filter = {
            'typeNames': list(type_names),
            'participantIds': list(participant_ids),
            'timestampStart': earliest_timestamp.isoformat(),
            'timestampEnd': latest_timestamp.isoformat(),
        }

        filtered_events = call(filter_events, deviceIds=[device_name], filter=events_filter)

        assert all_events == filtered_events

def test_improper_subset():
    """
    A subset constructed from the empty filter matches all events.
    """
    for device_name in TEST_DEVICE_NAMES:
        subset_name = 'test_improper_subset'
        try:
            call(create_subset, target={'oldDeviceId': device_name, 'newDeviceId': subset_name}, eventsFilter=None, contactsFilter=None)
            all_events = call(filter_events, deviceIds=[device_name], filter=None)
            subset_events = call(filter_events, deviceIds=[subset_name], filter=None)

            try:
                _compare_events_ignoring_device_ids(all_events['events'][0]['events'], subset_events['events'][0]['events'])
            except CompareFailed as e:
                print(f"Comparison failed while subsetting device {device_name}: {e}.")
                raise
        finally:
            call(delete_device, deviceId=subset_name)
