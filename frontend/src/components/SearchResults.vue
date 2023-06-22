<!-- 
This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
See LICENSE.txt for full details.
Copyright 2023 Telemarq Ltd
-->
<script setup>
import { ref, watch, computed } from 'vue'
import { eventsFilter, activeDevices } from '../store.js'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'

const { result: rawSearchResult, refetch: eventsRefetch } = useQuery( gql`
  query getEvents($deviceIds: [String]!, $filter: EventsFilter) {
	  events(deviceIds: $deviceIds, filter: $filter) {
	  	deviceId,
		events {
		  id
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
					name { first last display } phone email
				}
			  }
			  sender {
				  id
				  name { first last display }
				  phone
			  }
			  media {
				  mime_type
				  url
			  }
		  }
		}
	  }
  }
  `, {
	deviceIds: activeDevices,
	filter: eventsFilter
});

/* list of {typename: ..., events: ...} in order received. */
const chatSessions = ref({});  // Maps chat session key to list of participants

function getSessionKey(event) {
	return event.deviceId + ":" + event.providerName + ":" + event.sessionId;
}

const flex_basis = ref("100%");
const column_gap = ref("2px");

/* Computed property on the search results, to provide transformed data to be consumed by the UI:
 * - convert timestamps to DateTimes;
 * - store a delta since the last event;
 * - null out MesageEvent sessions if they're the same as the previous one.
*/
const searchResult = computed(() => {
	let result = {'events': []};

	if (rawSearchResult.value) {
		for(let events_for_device of rawSearchResult.value.events) {
			let efd = {'deviceId': events_for_device.deviceId, 'events': []};
			let lastSessionKey = null;
			let lastEvent = null;

			/* Post-process the server-supplied response */
			for(let event of events_for_device.events) {
				const newEvent = {...event};

				/* DateTimes arrive as strings. Convert them to Dates for easy manipulation and time comparisons. */
				newEvent.timestamp = new Date(event.timestamp);

				/* Remember the timestamp of  the last event, for friendlier date display */
				if(lastEvent !== null) {
					newEvent.previousTimestamp = lastEvent.timestamp;
				} else {
					newEvent.previousTimestamp = null;
				}

				/* We want to show chat participants in message sessions, but only once per run of
				 * messages -- so null out the session info if it's the same as the previous message.
				*/
				if(newEvent.__typename == "MessageEvent") {
					const key = getSessionKey(newEvent);
					if(key == lastSessionKey)
						newEvent.session = null;

					lastSessionKey = key;
				}

				efd.events.push(newEvent);

				lastEvent = newEvent;
			}
			result.events.push(efd);
		}
	}

	return result;
});

/* Watcher on the search results, to do work which doesn't require transforming the data:
 * - extract sessions from GUI events for later reference.
 * - set the column width of the per-device columns based on the number of devices.
*/
watch(rawSearchResult, (result) => {
	if (result) {
		for(let events_for_device of result.events) {
			for(let event of events_for_device.events) {
				/* Extract sessions from MessageEvents because they only appear once. */
				if(event.__typename == 'MessageEvent' && event.session != null) {
					/* This event includes a session reference so store it for later use. */
					chatSessions.value[getSessionKey(event)] = event.session;
				}
			}
		}
		/* Set the width of the GUI columns based on the number of devices being viewed. */
		flex_basis.value = "calc(" + 100 / activeDevices.value.length + "%" + " - " + column_gap.value + ")";
	}
});

function getSessionForMessageEvent(event) {
	return chatSessions.value[getSessionKey(event)];
}

/* Helper to retrieve chat session participants formatted for display. */
function getSessionParticipantsString(event) {
	const session = getSessionForMessageEvent(event);
	if(session == null) {
		return 'Unknown session';
	}

	let sessionText = [];

	for(let participant of session.participants) {
		let name;
		if(participant.name.display != null)
			name = participant.name.display;
		else if(participant.name.first != null && participant.name.last != null)
			name = participant.name.first + ' ' + participant.name.last;
		else
			name = 'Unknown';

		let text = name;
		if(participant.phone != null)
			text += ' (' + participant.phone + ')';
		else if(participant.email != null)
			text += ' (' + participant.email + ')';

		sessionText.push(text);
	}

	let participant_info = "";
	if(session.participants.length == 1) {
		participant_info += "Chat with " + sessionText[0];
	} else {
		if (session.name) {
			participant_info += "Group chat '" + session.name + "' with " + sessionText.join(', ');
		} else {
			participant_info += "Group chat with " + sessionText.join(', ');
		}
	}
	participant_info += " on " + event.providerFriendlyName
	return participant_info;
}

/* Is this MessageEvent a chat between the phone owner and a single other person? */
function isPrivateChat(event) {
	const session = getSessionForMessageEvent(event);
	if(session == null) {
		return false;
	}

	return session.participants.length == 1;
}

function formatEventTimestamp(event) {
	/* Show the full date and time if the time delta is null or greater than 24 hours, otherwise just the time. */
	const delta = event.previousTimestamp ? event.timestamp - event.previousTimestamp : null;

	if(event.previousTimestamp == null || delta == null || delta > 24 * 60 * 60 * 1000
			|| event.previousTimestamp.getDate() != event.timestamp.getDate()) {
		return event.timestamp.toLocaleDateString() + " " + event.timestamp.toLocaleTimeString();
	} else {
		return event.timestamp.toLocaleTimeString();
	}
}

const roughly_the_same_ms = 1000;

function * eventsRowGenerator() {
	/* Repeatedly return a row of Events to display.

	   We want events from different devices to line up chronologically, so we maintain a list of
	   pointers into the current event from each device. For each row, we find the oldest event timestamp
	   from the current list and return all device events which have that timestamp, advancing the pointers
	   for those devices which produced an event this row. We rely on the events for each device being sorted
	   by timestamp.

	   When we have no events to display from any device we're done.

	   Timestamps are compared roughly (to roughly_the_same_ms) to attempt to group concurrent chats
	   despite network latency and clock drift.
	*/

	const num_devices = searchResult.value ? searchResult.value.events.length : 0;
	let pointers = new Array(num_devices).fill(0);
	let num_empty = 0;

	while(num_empty < num_devices) {
		let row = [];
		let minTime = null;
		num_empty = 0;

		/* Create a row of events containing one event from each device. */
		for(let deviceIdx = 0; deviceIdx < num_devices; deviceIdx++) {
			let deviceEvents = searchResult.value.events[deviceIdx].events;
			if(pointers[deviceIdx] < deviceEvents.length) {
				const event = deviceEvents[pointers[deviceIdx]];
				if(minTime == null || event.timestamp < minTime) {
					minTime = event.timestamp;
				}
				row.push(event);
				pointers[deviceIdx]++;
			} else {
				row.push(null);
				num_empty++;
			}
		}

		if(minTime == null) {
			/* No events found. */
			break;
		}

		const minTime_rough = Math.floor(minTime.getTime() / roughly_the_same_ms) * roughly_the_same_ms;

		/* Null out events that occured before the earliest event in this row. */
		for(let deviceIdx = 0; deviceIdx < num_devices; deviceIdx++) {
			const event = row[deviceIdx];
			if(event !== null) {
				const eventTime_rough = Math.floor(event.timestamp.getTime() / roughly_the_same_ms) * roughly_the_same_ms;
				if(eventTime_rough > minTime_rough) {
					row[deviceIdx] = null;

					/* roll back the pointer so we can re-use this event in the next row. */
					pointers[deviceIdx]--;
				}
			}
		}

		if(num_empty < num_devices) {
			yield row;
		}
	}
}

</script>

<template>
	<div id="view">
		<button id="refresh" @click="eventsRefetch()">&#128472;</button>
		<div class="rowContainer rowHeader">
			<div v-for="device in activeDevices" class="event eventHeader"><span class="deviceName">{{ device }}</span></div>
		</div>
		<div v-if="searchResult" v-for="eventRow in eventsRowGenerator()" class="rowContainer">
			<template v-for="event in eventRow">
				<div v-if="event !== null" class="event">
					<div :class="event.__typename">
						<div v-if="event.__typename == 'MessageEvent' && event.session !== null" class="sessioninfo">
							{{ getSessionParticipantsString(event) }}
						</div>
						<div class="message" v-if="event.__typename == 'MessageEvent'" :class="{ from_me: event.fromMe }">
							<div class="message_body">
								<div v-if="event.media" class="message_media">
									<video v-if="event.media.mime_type.startsWith('video')" controls>
										<source :src="event.media.url" :type="event.media.mime_type"/>
									</video>
									<img v-else :src="event.media.url" />
								</div>
								{{ event.text }}
							</div>
							<div class="metadata">
								<span class="sender" v-if="!event.fromMe && event.sender && !isPrivateChat(event)">
									<span v-if="event.sender.name.display">{{ event.sender.name.display }}</span>
									<span v-else-if="event.sender.name.first">{{ event.sender.name.first }} {{ event.sender.name.last }}</span>
									<span v-if="event.sender.phone"> ({{ event.sender.phone }})</span>
									&nbsp;
								</span>
								<span class="timestamp"> {{formatEventTimestamp(event)}}</span>
							</div>
						</div>
					</div>
				</div>
				<div v-else class="event"></div>
			</template>
		</div>
		<div v-if="searchResult.events.length === 0" class="center text-box">
			Select one or more devices at the top left to begin.
		</div>
	</div>
</template>

<style scoped>

.center {
	margin: auto;
	margin-top: 15%;
	width: 30em;
	text-align: center;
}

.rowContainer {
	display: flex;
	flex-direction: row;
	column-gap: v-bind(column_gap);
}

.rowHeader {
	font-weight: bold;
	position: sticky;
	top: 0;
}

.event {
	display: inline-block;
	flex-basis: v-bind(flex_basis);
	flex-grow: 0;
	flex-shrink: 0;
}

.eventHeader {
	background: white;
}

.eventHeader .deviceName {
	padding: 0.5em;
	font-weight: bold;
}

.MessageEvent {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
}

.MessageEvent>.from_me {
	align-self: flex-end;
}

.sender {
	font-size: 0.8em;
	color: #666;
}

.sessioninfo {
	font-size: 0.8em;
	margin: 0.5em;
	padding-left: 0;
	color: #444;
}

.message {
	margin: 0.5em;
	flex: 0;
	padding-left: 1em;
}

.message_body {
	padding: 1em;
	background-color: var(--theme-message-bg);
	color: var(--theme-message-fg);
	border-radius: 20px;
}

.from_me>.message_body {
	background-color: var(--theme-message-from_me-bg);
	color: var(--theme-message-from_me-fg);
}

.timestamp {
	font-size: 12px;
	color: #888;
}


.device {
	font-size: 12px;
	color: #aaa;
}

#refresh {
	position: fixed;
	top: 2px;
	right: 2px;
	width: 3em;
	z-index: 1;
}

.message_media img {
	max-width: 100%;
}

</style>
