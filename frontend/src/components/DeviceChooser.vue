<!-- 
This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
See LICENSE.txt for full details.
Copyright 2023 Telemarq Ltd
-->

<script setup>
import { watch, ref, nextTick } from 'vue'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { devices, activeDevices, deleteDevice, setDeviceSelected, devicesGqlRefetch } from '../store.js'
import gql from 'graphql-tag'

/* When activeDevices changes, update the check boxes. */
watch(activeDevices, (newVal, oldVal) => {
	nextTick(() => {
		devices.value.forEach(device => {
			const cb = document.getElementById('device-' + device.id);
			if(!cb) return;

			cb.checked = newVal.includes(device.id);
		});
	});
});

async function toggleDeviceActive(id) {
	const cb = document.getElementById('device-' + id);
	if(!cb) return;

	await setDeviceSelected(id, cb.checked);
}

</script>

<template>
	<div id="view">
		<h1>Devices</h1>
		<div v-for="device in devices">
			<input type="checkbox" :id="'device-' + device.id" :key="device.id" :value="device.id"
				:label="device.id" @click="toggleDeviceActive(device.id)" :disabled="device.is_locked" />
			<label :class="{ locked: device.is_locked }" :for="'device-' + device.id">{{ device.id }}</label>
			<span class="country_code">{{ device.country_code }}</span>
			<div class="delete" v-if="device.is_subset && !device.is_locked" @click="deleteDevice(device.id)">&#10060;</div>
		</div>
	</div>
</template>

<style scoped>

.delete {
	display: inline-block;
	color: red;
	font-size: 8px;
	text-align: center;
	float: right;
	cursor: pointer;
}

.country_code {
	padding-left: 0.5em;
	font-size: 0.7em;
	color: #888;
	cursor: default;
}

label.locked {
	color: #888;
	cursor: default;
}

</style>
