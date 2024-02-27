
import { ref, watch, computed } from 'vue'
import { eventsFilter, activeDevices, rawEventsSearchResult, eventsRefetch } from './store.js'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'

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

const column_gap = ref("2px");
const grid_template_columns = ref("repeat(1, 1fr)");

/* Computed property on the search results, to provide transformed data to be consumed by the UI:
 * - convert timestamps to DateTimes;
 * - store a delta since the last event;
 * - null out MessageEvent sessions if they're the same as the previous one.
*/
export const searchResult = computed(() => {
	let result = {'deviceIds': [], 'providers': [], 'events': []};
	let lastEventForDevice = {};
	let lastSessionKeyForDevice = {};

	if (rawEventsSearchResult.value) {
		result['deviceIds'] = rawEventsSearchResult.value.events.deviceIds;
		result['providers'] = rawEventsSearchResult.value.events.providers;
		result['messageSessions'] = rawEventsSearchResult.value.events.messageSessions;

		for(let session of rawEventsSearchResult.value.events.messageSessions) {
			chatSessions.value[session.sessionId] = new ChatSession(session.sessionId, session.name, session.participants, session.providerFriendlyName);
		}

		for(let event of rawEventsSearchResult.value.events.events) {
			/* Post-process the server-supplied response */
			const newEvent = {...event};

			/* DateTimes arrive as strings. Convert them to Dates for easy manipulation and time comparisons. */
			newEvent.timestamp = new Date(event.timestamp);

			/* Remember the timestamp of  the last event, for friendlier date display */
			if(lastEventForDevice[event.deviceId] !== undefined) {
				newEvent.previousTimestamp = lastEventForDevice[event.deviceId].timestamp;
			} else {
				newEvent.previousTimestamp = null;
			}

			if(newEvent.__typename == "MessageEvent") {
				/* Create the chat session if it doesn't exist */
				if(newEvent.sessionId == lastSessionKeyForDevice[event.deviceId]) {
					/* We've seen this session, so don't store it again. The GUI uses this to determine
					   when a new session starts */
					newEvent.session = null;
				} else {
					/* Overwrite it with the session object */
					newEvent.session = chatSessions.value[newEvent.sessionId];
				}

				lastSessionKeyForDevice[event.deviceId] = newEvent.sessionId;
			}

			result.events.push(newEvent);
			lastEventForDevice[event.deviceId] = newEvent;
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

	   We want events from different devices to line up chronologically. RIME guarantees that events
	   are ordered by timestamp.

	   We generate a row at a time based on the timestamp, and start a new row if:
	     - the timestamp of the event is more than roughly_the_same_ms after the previous event, or
		 - the event is for a device we've already seen.
	*/

	if(!searchResult.value)
		return;

	const empty_row = Array(searchResult.value.deviceIds.length).fill(null);
	const row_is_empty = (row) => row.every((event) => event == null);

	let row = empty_row.slice();
	let minTime = searchResult.value.events.length > 0 ? searchResult.value.events[0].timestamp : null;

	for(let event of searchResult.value.events) {
		const ts_delta = Math.abs(event.timestamp.getTime() - minTime.getTime());
		const device_idx = searchResult.value.deviceIds.indexOf(event.deviceId);

		if(ts_delta > roughly_the_same_ms || row[device_idx] != null) {
			/* This event is too far away from the previous one, or we've already seen an event for this device.
			   Yield the current row and start a new one. */
			yield row;
			row = empty_row.slice();
			minTime = event.timestamp;
		}

		row[device_idx] = event;
	}

	if(!row_is_empty(row)) {
		yield row;
	}
}

