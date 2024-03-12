
<template>
  <div>
    <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div>

    <div v-else>
      <div class="center-container">
        <div class="date-picker">
          <label for="startDatePicker">start date:</label>
          <input type="date" id="startDatePicker" v-model="startDate">
          <label for="endDatePicker">end date:</label>
          <input type="date" id="endDatePicker" v-model="endDate">
          <button id="zoomToButton" @click="zoomTo">Zoom To</button>
          <button id="fitButton" @click="fit">Fit to Container</button>
          <div class="info-icon" @mouseover="showInfoBox = true" @mouseleave="showInfoBox = false">
            <span class="icon">?</span>
            <div class="info-box" v-show="showInfoBox">
              Information about the date range...
            </div>
          </div>
        </div>
      </div>

      <div class="time-range">
        <div>{{ timeRange }}</div>
        <label for="timeRangeSelect">Select Time Range:</label>
        <select id="timeRangeSelect" class ="dropdown-hours" v-model="selectedTimeRange">
          <option value="1800000">30 minutes</option>
          <option value="3600000">1 hour</option>
          <option value="7200000">2 hours</option>
          <option value="10800000">3 hours</option>
        </select>
      </div>

      <div class="container">
        <div ref="timeline" class="timeline"></div>
      </div>

      <div id="legendContainer" class="legend-container"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import * as anychart from 'anychart';
import { activeDevices } from '../store.js';
import { searchResult } from '../eventsdata.js'

const timeRange = ref('');
const timeline = ref(null);
const messagesSet = ref([]);
const startDate = ref('');
const endDate = ref('');
var startOfMonthTimestamp = ref(null);
var endOfMonthTimestamp = ref(null);
const showInfoBox = ref(false);
const selectedTimeRange = ref(7200000);

const zoomTo = () => {

  if (!startDate.value || !endDate.value) {
    alert('Null value of dates present');
  }
  else {
    const selectedStartDate = new Date(startDate.value).toISOString().slice(0, -1);
    const selectedEndDate = new Date(endDate.value).toISOString().slice(0, -1);

    if (new Date(selectedEndDate) > new Date(endOfMonthTimestamp.value) ||
      new Date(selectedStartDate) < new Date(startOfMonthTimestamp.value) ||
      new Date(selectedStartDate) > new Date(endOfMonthTimestamp.value) ||
      new Date(selectedEndDate) < new Date(startOfMonthTimestamp.value)) {
      alert('Selected dates are not within the range of the search result.');
    } else {
      console.log("Safe to zoom")
    }
  }
};

const applyFilter = () => {
};

const generateColor = (index) => {
  const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
  return colors[index % colors.length];
}

watch(searchResult, (result) => {
  if (!result) return;

  const events = result.events;

  if (events.length === 0) return;

  const sortedEvents = events.sort((a, b) => a.timestamp - b.timestamp);
  const earliestEvent = sortedEvents[0];
  const latestEvent = sortedEvents[sortedEvents.length - 1];
  const earliestTimestamp = new Date(earliestEvent.timestamp);
  const latestTimestamp = new Date(latestEvent.timestamp);

  startOfMonthTimestamp.value = startOfMonth(earliestTimestamp);
  endOfMonthTimestamp.value = endOfMonth(latestTimestamp);

  timeRange.value = `Time Range: ${startOfMonthTimestamp.value.toLocaleString()} - ${endOfMonthTimestamp.value.toLocaleString()}`;
});

const startOfMonth = (date) => {
  const nextMonth = new Date(date);
  nextMonth.setMonth(nextMonth.getMonth() + 1);
  const roundedDate = new Date(Math.ceil(nextMonth.getTime() / (10 * 60 * 1000)) * (10 * 60 * 1000));
  return roundedDate.toISOString().slice(0, -1);
}

const endOfMonth = (date) => {
  const nextMonth = new Date(date);
  nextMonth.setMonth(nextMonth.getMonth() + 1);
  const roundedDate = new Date(Math.ceil(nextMonth.getTime() / (10 * 60 * 1000)) * (10 * 60 * 1000));
  return roundedDate.toISOString().slice(0, -1);
}

watch([selectedTimeRange, searchResult], ([timeRange, result]) => {
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
        const isWithinTwoHours = timeDiff <= timeRange;

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

    const Hours = timeRange;

    let events = dataExample
    rangeData = [];

    let providerName = events[0].name;
    let deviceName = events[0].deviceName;
    let rangeStart = events[0].start;
    let rangeEnd = events[0].end;

    for (let i = 1; i < events.length; i++) {
      const event = events[i];
      const timeDifference = event.start - rangeEnd;
      if (event.name === providerName && event.deviceName === deviceName && timeDifference <= Hours) {
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
    const chartDataWithoutFirstElement = subArray.slice(1);
    const data = chartDataWithoutFirstElement.map(event => [event[0], event[1], event[2]]);
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
.dropdown-hours{
  width: 100px
}
.time-range {
  display: flex;
  margin-right: 20px;
  align-items: center;
}

.center-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-icon {
  position: relative;
  display: inline-block;
}

.info-icon:hover .info-box {
  display: block;
}

.icon {
  display: inline-block;
  width: 40px;
  /* Increased width */
  height: 40px;
  /* Increased height */
  border-radius: 50%;
  background-color: #ccc;
  color: #fff;
  text-align: center;
  line-height: 40px;
  /* Adjusted line height */
  cursor: pointer;
  margin-right: 20px;
  /* Added margin */
}

.info-box {
  position: absolute;
  top: -60px;
  left: -100px;
  width: 200px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: none;
}

button,
label {
  margin: 10px 5px;
}

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 100px);
  width: 100%;
}

.centered-timeline {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}


#fitButton {
  right: 10px;
}

#dateLabel1 {
  margin: 0;
  font-style: italic;
}

#dateLabel2 {
  margin: 0;
  font-style: italic;
}

.center {
  margin: auto;
  margin-top: 15%;
  width: 30em;
  text-align: center;
}

.legend-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 40px;
}

#legendContainer {
  margin-bottom: 30px;

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
