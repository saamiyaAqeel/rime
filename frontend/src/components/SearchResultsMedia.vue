<!-- 
This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
See LICENSE.txt for full details.
Copyright 2023 Telemarq Ltd
-->
<script setup>
import { activeDevices, rawEventsSearchResult, eventsSearchResultById } from '../store.js'
import SearchResultMediaEvent from './SearchResultMediaEvent.vue'

import { watch, ref } from 'vue'

const menuitems = ref(null);
const menuDownloadUrl = ref(null);

const toggleMenu = function(event) {
	const menu = event.target.closest('.menu');

	if(menuitems.value.parentNode) {
		menuitems.value.parentNode.removeChild(menuitems.value);
		menuitems.value.style.display = 'none';
	}

	if(menu) {
		if(menu.classList.contains('open')) {
			menu.classList.remove('open');
		} else {
			menu.classList.add('open');
			menu.appendChild(menuitems.value);
			menuitems.value.style.display = 'block';

			menuDownloadUrl.value = eventsSearchResultById.value[menu.dataset.eventid].url;
		}

	}
	/* Close all other menus */
	const menus = document.querySelectorAll('.menu.open');
	for(const otherMenu of menus) {
		if(otherMenu == menu) {
			continue;
		}
		otherMenu.classList.remove('open');
	}
}

</script>

<template>
	<div class="grid" v-if="rawEventsSearchResult">
		<div id="menuitems" ref="menuitems">
			<ul>
				<li><a :href="menuDownloadUrl" target="_blank">Download</a></li>
			</ul>
		</div>
		<template v-for = "event in rawEventsSearchResult.events.events">
			<div v-if="event && event.__typename == 'MediaEvent'" class="gridElement">
				<div class="menu" :data-eventid="event.id"><div class="burger" @click="toggleMenu"> &vellip; </div></div>
				<video v-if="event.mime_type.startsWith('video')" controls>
					<source :src="event.url" :type="event.mime_type"/>
				</video>
				<img v-else :src="event.url" />
			</div>
		</template>
	</div>
</template>


<style scoped>
.grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
	grid-gap: 1px;
}

.gridElement {
	position: relative; /* for the menu */
}

.menu {
	position: absolute;
	top: 0;
	right: 0;
	text-align: right;
	cursor: pointer;
	z-index: 1;
}

.menu.open {
	background-color: #eeea;
}

#menuitems {
	display: none;
	position: relative;
	top: 0;
	right: 0;
	padding: 0.5em;
	z-index: 1;
}

#menuitems ul {
	list-style-type: none;
	margin: 0;
	padding: 0;
}

img {
	max-width: 100%;
}

video {
	max-width: 100%;
}

</style>
