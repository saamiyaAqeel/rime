<!-- 
This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
See LICENSE.txt for full details.
Copyright 2023 Telemarq Ltd
-->
<script setup>
import { activeDevices, rawEventsSearchResult } from '../store.js'
import SearchResultMediaEvent from './SearchResultMediaEvent.vue'

import { watch } from 'vue'

</script>

<template>
	<div class="grid" v-if="rawEventsSearchResult">
		<template v-for = "event in rawEventsSearchResult.events.events">
			<div v-if="event && event.__typename == 'MediaEvent'" class="gridElement">
				<video v-if="event.mime_type.startsWith('video')" controls>
					<source :src="event.url" :type="event.media.mime_type"/>
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

img {
	max-width: 100%;
}

</style>
