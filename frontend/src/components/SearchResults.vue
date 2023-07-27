<!-- 
This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
See LICENSE.txt for full details.
Copyright 2023 Telemarq Ltd
-->
<template>
	<div>
		<button id="refresh" @click="eventsRefetch()">&#128472;</button>
		<div class="searchResultsTable">
			<div v-for="device in activeDevices" class="header"><span class="deviceName">{{ device }}</span></div>
			<div v-if="searchResult" v-for="eventRow in eventsRowGenerator()" class="row">
				<template v-for="event in eventRow">
					<div v-if="event !== null" class="event" :class="event.__typename">
						<SearchResultMessageEvent v-if="event.__typename == 'MessageEvent'" :event="event" />
					</div>
					<div v-else class="event"></div>
				</template>
			</div>
		</div>
		<div v-if="activeDevices.length === 0" class="center text-box">
			Select one or more devices at the top left to begin.
		</div>
	</div>
</template>
<style scoped>

.searchResultsTable {
	display: grid;
	grid-template-columns: v-bind(grid_template_columns);
}

.searchResultsTable .header {
	font-weight: bold;
	top: 0;
	position: sticky;
	background: white;
}

.searchResultsTable>.row {
	display: contents;
}

.center {
	margin: auto;
	margin-top: 15%;
	width: 30em;
	text-align: center;
}

.event {
	display: inline-block;
}

.eventHeader {
	background: white;
}

.eventHeader .deviceName {
	padding: 0.5em;
	font-weight: bold;
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

</style>

<script setup>
import { ref, watch, computed } from 'vue'
import { eventsFilter, activeDevices, rawEventsSearchResult, eventsRefetch } from '../store.js'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'

import SearchResultMessageEvent from './SearchResultMessageEvent.vue'

class ChatSession {
	constructor(sessionId, name, participants, providerFriendlyName) {
		this.sessionId = sessionId;
		this.name = name;
		this.participants = participants;
		this.providerFriendlyName = providerFriendlyName;
	}

	/* Helper to retrieve chat session participants formatted for display. */
	getParticipantsString() {
		let sessionText = [];

		for(let participant of this.participants) {
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
		if(this.participants.length == 1) {
			participant_info += "Chat with " + sessionText[0];
		} else {
			if (this.name) {
				participant_info += "Group chat '" + this.name + "' with " + sessionText.join(', ');
			} else {
				participant_info += "Group chat with " + sessionText.join(', ');
			}
		}
		participant_info += " on " + this.providerFriendlyName;
		return participant_info;
	}

	isPrivateChat() {
		return this.participants.length == 1;
	}
}

/* list of {typename: ..., events: ...} in order received. */
const chatSessions = ref({});  // Maps chat session key to list of participants

function getSessionKey(event) {
	return event.deviceId + ":" + event.providerName + ":" + event.sessionId;
}

const column_gap = ref("2px");
const grid_template_columns = ref("repeat(1, 1fr)");

/* Computed property on the search results, to provide transformed data to be consumed by the UI:
 * - convert timestamps to DateTimes;
 * - store a delta since the last event;
 * - null out MesageEvent sessions if they're the same as the previous one.
*/
const searchResult = computed(() => {
	let result = {'events': []};

	if (rawEventsSearchResult.value) {
		for(let events_for_device of rawEventsSearchResult.value.events) {
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

				if(newEvent.__typename == "MessageEvent") {
					const key = getSessionKey(newEvent);

					/* Create the chat session if it doesn't exist */
					if(!(key in chatSessions.value)) {
						chatSessions.value[key] = new ChatSession(newEvent.sessionId, newEvent.session.name,
																  newEvent.session.participants, newEvent.providerFriendlyName);
					}

					if(key == lastSessionKey) {
						/* We've seen this session, so don't store it again. The GUI uses this to determine
						   when a new session starts */
						newEvent.session = null;
					} else {
						/* Overwrite it with the session object */
						newEvent.session = chatSessions.value[key];
					}

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
watch(rawEventsSearchResult, (result) => {
	if (!result)
		return;

	/* Set the width of the GUI columns based on the number of devices being viewed. */
	/* TODO just put this at outer level? Yes, and/or use CSS grid. */
	grid_template_columns.value = `repeat(${activeDevices.value.length}, minmax(0, 1fr))`;
});

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
