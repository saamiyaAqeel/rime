<template>
  <!-- <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div> -->
  <!-- <div class="timeline-container">
  <div ref="timeline"></div> -->
  <!-- <div id="legendContainer"></div> -->
  <!-- </div> -->

  <div>

     <!-- <div class="filter-container">
       <label for="start-date">Start Date:</label>
      <input type="date" id="start-date" v-model="startDate">
      <label for="start-time">Start Time:</label>
      <input type="time" id="start-time" v-model="startTime">
      <label for="end-date">End Date:</label>
      <input type="date" id="end-date" v-model="endDate">
      <label for="end-time">End Time:</label>
      <input type="time" id="end-time" v-model="endTime">
      <button @click="applyFilter">Apply</button> 
    </div>  -->

    <div class="container">
      <div ref="timeline"></div>
    </div>

    <div id="legendContainer" class="legend-container"></div>
    <!-- <div class="container" v-if="hasRangeData">
      <div ref="timeline"></div>
    </div> -->
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
const legendItems = ref([]);

const applyFilter = () => {
};

const generateColor = (index) => {
  const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
  return colors[index % colors.length];
}

watch(searchResult, (result) => {
  if (!result)
    return;
  messagesSet.value = []

  if (activeDevices.value.length > 0) {
    const set = result.events;
    if (set.length === 0) return;

    const messagesSet = [];
    result.events.forEach(event => {
      messagesSet.push(event);
    });

    const sortedEventData = messagesSet.sort((a, b) => a.timestamp - b.timestamp);

    var rangeData = [];
    const momentData = [];
    const dataExample = [];

    const groups = {};
    sortedEventData.forEach(event => {
      const { providerName, timestamp } = event;
      if (!groups[providerName]) {
        groups[providerName] = [];
      }
      groups[providerName].push(event);
    });

    const deviceIds = [];
    result.events.forEach(event => {
      deviceIds.push(event.deviceId); 
    });

    const uniqueDeviceIds = Array.from(new Set(deviceIds)); 

    for (const providerName in groups) {
      const providerEvents = groups[providerName];
      let rangeStart = providerEvents[0].timestamp;
      let rangeEnd = providerEvents[0].timestamp;
      let device = providerEvents[0].deviceId

      for (let i = 1; i < providerEvents.length; i++) {
        const currentEvent = providerEvents[i];
        const prevEvent = providerEvents[i - 1];

        const timeDiff = currentEvent.timestamp - prevEvent.timestamp;
        const isWithinTwoHours = timeDiff <= 2 * 60 * 60 * 1000;

        if (isWithinTwoHours) {
          dataExample.push({
            deviceName: device,
            name: providerName,
            start: prevEvent.timestamp,
            end: currentEvent.timestamp
          });
        } else {
          momentData.push({
            x: prevEvent.timestamp,
            y: `${providerName} - Range End`
          });

          rangeStart = currentEvent.timestamp;
          rangeEnd = currentEvent.timestamp;
        }
      }

      momentData.push({
        x: rangeEnd,
        y: `${providerName} - Range End`
      });
    }

    const twoHours = 2 * 60 * 60 * 1000;

    let events = dataExample
    rangeData = [];

    let providerName = events[0].name;
    let deviceName = events[0].deviceName;
    let rangeStart = events[0].start;
    let rangeEnd = events[0].end;

    for (let i = 1; i < events.length; i++) {
      const event = events[i];
      const timeDifference = event.start - rangeEnd;
      if (event.name === providerName && event.deviceName === deviceName && timeDifference <= twoHours) {
        rangeEnd = event.end;
      } else {
        rangeData.push([providerName, deviceName, rangeStart, rangeEnd]);
        providerName = event.name;
        deviceName = event.deviceName;
        rangeStart = event.start;
        rangeEnd = event.end;
      }
    }

    rangeData.push([providerName, deviceName, rangeStart, rangeEnd]);

    const splitRangeData = [];
    let currentSubArray = [rangeData[0][1]];

    for (let i = 0; i < rangeData.length; i++) {
      const currentEvent = rangeData[i];
      const nextEvent = rangeData[i + 1];

      currentSubArray.push([currentEvent[0], currentEvent[2], currentEvent[3]]);

      if (!nextEvent || nextEvent[0] !== currentEvent[0]) {
        splitRangeData.push(currentSubArray);
        currentSubArray = nextEvent ? [nextEvent[1]] : [];
      }
    }

    let decemberSubArray = []
    let decemberData = [];

    console.log(splitRangeData)

    decemberData = splitRangeData.flatMap(subArray => {
      const providerName = subArray[0];

      const decemberSubArray = subArray.slice(1).reduce((acc, event) => {
        const [startTimeMonth, endTimeMonth] = [new Date(event[1]).getMonth(), new Date(event[2]).getMonth()];
        if (startTimeMonth === 11 || endTimeMonth === 11) acc.push([providerName, event[0], event[1], event[2]]);
        return acc;
      }, []);

      return decemberSubArray;
    });

    const deviceIdColorPairs = getColorByTitle(uniqueDeviceIds);
    anyTimeline(splitRangeData, momentData, deviceIdColorPairs);
    createLegend(deviceIdColorPairs);
  }
});


const anyTimeline = (chartData, momentData, deviceIdColorPairs) => {
  const chart = anychart.timeline();
  chartData.forEach((subArray, index) => {
    const deviceName = subArray[0];
    const deviceColor = deviceIdColorPairs.find(pair => pair.deviceId === deviceName)?.color;
    console.log(deviceColor)
    const chartDataWithoutFirstElement = subArray.slice(1);
    const data = chartDataWithoutFirstElement.map(event => [event[0], event[1], event[2]]);
    console.log(data);
    const rangeSeries = chart.range(data);
    rangeSeries.normal().fill(deviceColor);
    rangeSeries.normal().stroke(deviceColor);
  });
  chart.moment(momentData)
  chart.container(timeline.value);
  chart.scroller().enabled(true);
  var axis = chart.axis();
  axis.height(25);
  chart.draw();
  timeline.value.classList.add('centered-timeline');

}

const createLegend = (deviceIdColorPairs) => {
  const legendContainer = document.getElementById('legendContainer');

  deviceIdColorPairs.forEach((pair) => {
    const legendItem = document.createElement('div');
    legendItem.style.display = 'flex';

    const square = document.createElement('div');
    square.style.width = '20px';
    square.style.height = '20px';
    square.style.backgroundColor = pair.color;
    square.style.marginRight = '5px';

    const label = document.createElement('div');
    label.innerHTML = pair.deviceId;

    legendItem.appendChild(square);
    legendItem.appendChild(label);

    legendContainer.appendChild(legendItem);
  });
};


const getColorByTitle = (uniqueDeviceIds) => {
  const colors = ['#ff0000', '#00ff00', '#0000ff', '#808080'];
  const deviceIdColorPairs = [];

  uniqueDeviceIds.forEach((deviceId, index) => {
    const colorIndex = index % colors.length;
    const color = colors[colorIndex];
    deviceIdColorPairs.push({ deviceId: deviceId, color: color });
  });

  return deviceIdColorPairs;
};


onMounted(() => {

});

</script>

<style scoped>
.legend-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 40px;
  /* Adjust spacing between legend items */
}

#legendContainer {
  margin-bottom: 30px;

}

.container {
  /* justify-content: center;
  align-items: center;
  width: 100%;
  height: 80%; */

  /* margin-top: 70px;
  margin-bottom: 70px; */

  /* width: 100%;
  height: 100%;
  margin: 0;
  padding: 0; */

  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; 
  width: 100%; 
  margin: 0;
  padding: 0;  

}

.centered-timeline {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}


.filter-container {
  margin-top: 100px;
  margin-bottom: 70px;
  margin-left: 100px;
}

.filter-container label,
.filter-container input,
.filter-container button {
  margin-right: 10px;
}
</style>
