
<template>
  <!-- <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div> -->
  <!-- <div class="timeline-container">
  <div ref="timeline"></div> -->
  <!-- <div id="legendContainer"></div> -->
  <!-- </div> -->
  <div>
    <div class="filter-container">
      <label for="start-date">Start Date:</label>
      <input type="date" id="start-date" v-model="startDate">
      <label for="start-time">Start Time:</label>
      <input type="time" id="start-time" v-model="startTime">
      <label for="end-date">End Date:</label>
      <input type="date" id="end-date" v-model="endDate">
      <label for="end-time">End Time:</label>
      <input type="time" id="end-time" v-model="endTime">
      <button @click="applyFilter">Apply</button>
    </div>

    <!-- <div class="container">
      <div ref="timeline"></div>
    </div> -->
    <div class="container" v-if="hasRangeData">
      <div ref="timeline"></div>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import * as anychart from 'anychart';
import { activeDevices } from '../store.js';
import { searchResult } from '../eventsdata.js'

const timeline = ref(null);
const messagesSet = ref([]);
const startDate = ref('');
const startTime = ref('');
const endDate = ref('');
const endTime = ref('');
const hasRangeData = ref(false);

const applyFilter = () => {
};

watch(searchResult, (result) => {
  // if (!result)
  //   return;
  // console.log("HELLO I AM HERE")
  // messagesSet.value = []

  // if (activeDevices.value.length > 0) {
  //   const messagesSet = [];
  //   result.events.forEach(event => {
  //     messagesSet.push(event);
  //   });

  //   const sortedEventData = messagesSet.sort((a, b) => a.timestamp - b.timestamp);

  //   var rangeData = [];
  //   const momentData = [];
  //   const dataExample = [];

  //   const groups = {};
  //   sortedEventData.forEach(event => {
  //     const { providerName, timestamp } = event;
  //     if (!groups[providerName]) {
  //       groups[providerName] = [];
  //     }
  //     groups[providerName].push(event);
  //   });

  //   for (const providerName in groups) {
  //     const providerEvents = groups[providerName];
  //     let rangeStart = providerEvents[0].timestamp;
  //     let rangeEnd = providerEvents[0].timestamp;

  //     for (let i = 1; i < providerEvents.length; i++) {
  //       const currentEvent = providerEvents[i];
  //       const prevEvent = providerEvents[i - 1];

  //       const timeDiff = currentEvent.timestamp - prevEvent.timestamp;
  //       const isWithinTwoHours = timeDiff <= 2 * 60 * 60 * 1000;

  //       if (isWithinTwoHours) {
  //         dataExample.push({
  //           name: providerName,
  //           start: prevEvent.timestamp,
  //           end: currentEvent.timestamp
  //         });
  //       } else {
  //         momentData.push({
  //           x: prevEvent.timestamp,
  //           y: `${providerName} - Range End`
  //         });

  //         rangeStart = currentEvent.timestamp;
  //         rangeEnd = currentEvent.timestamp;
  //       }
  //     }

  //     rangeData.push({
  //       name: providerName,
  //       start: rangeStart,
  //       end: rangeEnd
  //     });

  //     momentData.push({
  //       x: rangeEnd,
  //       y: `${providerName} - Range End`
  //     });
  //   }

  //   const twoHours = 2 * 60 * 60 * 1000; 

  //   let events = dataExample
  //   rangeData = [];
  //   let providerName = events[0].name;
  //   let rangeStart = events[0].start;
  //   let rangeEnd = events[0].end;

  //   for (let i = 1; i < events.length; i++) {
  //     const event = events[i];
  //     const timeDifference = event.start - rangeEnd;

  //     if (event.name === providerName && timeDifference <= twoHours) {
  //       rangeEnd = event.end;
  //     } else {
  //       rangeData.push([providerName, rangeStart, rangeEnd]);
  //       providerName = event.name;
  //       rangeStart = event.start;
  //       rangeEnd = event.end;
  //     }
  //   }

  //   rangeData.push([providerName, rangeStart, rangeEnd]);

  //   const decemberRangeData = rangeData.filter(event => {
  //     const eventDate = new Date(event[1]);
  //     const month = eventDate.getMonth() + 1; 
  //     const year = eventDate.getFullYear();
  //     return month === 12 && year === 2022;
  //   });

  //   hasRangeData.value = rangeData.length > 0;

  //   if (hasRangeData.value) {
  //     anyTimeline(rangeData);
  //   }

  // }
});

const anyTimeline = (chartData) => {
  const chart = anychart.timeline();
  chart.range(chartData);
  console.log(chartData)
  chart.container(timeline.value);
  chart.scroller().enabled(true);
  console.log("THE DATA HAS CHANGED")
  chart.draw();
}


// const getColorByTitle = (title) => {
//   if (title.includes('A')) {
//     return '#ff0000';
//   } else if (title.includes('B')) {
//     return '#00ff00';
//   } else if (title.includes('C')) {
//     return '#0000ff';
//   } else {
//     return '#808080';
//   }
// };

// const createLegend = (timelineData, chart) => {
//   const legendContainer = document.getElementById('legendContainer');

//   for (let i = 0; i < timelineData.length; i++) {
//     const legendItem = document.createElement('div');
//     legendItem.style.display = 'flex';

//     const square = document.createElement('div');
//     square.style.width = '20px';
//     square.style.height = '20px';
//     square.style.backgroundColor = getColorByTitle(timelineData[i].title);
//     square.style.marginRight = '5px';

//     const label = document.createElement('div');
//     label.innerHTML = timelineData[i].title;

//     legendItem.appendChild(square);
//     legendItem.appendChild(label);

//     legendContainer.appendChild(legendItem);
//   }
// };



onMounted(() => {

});

</script> 

<style scoped>
#legendContainer {
  margin-top: 20px;
}

.container {
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* .container {
  text-align: center; 
}

.content {
  display: inline-block; 
} */

.filter-container {
  margin-top: 100px;
  margin-bottom: 40px;
  margin-left: 100px;
}

.filter-container label,
.filter-container input,
.filter-container button {
  margin-right: 10px;
}
</style>


