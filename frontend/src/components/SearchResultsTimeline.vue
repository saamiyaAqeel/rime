
<template>
  <div class="center">
    <!-- <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div> -->

    <div class="timeline-container">
      <div ref="timeline"></div>
      <!-- <div id="legendContainer"></div> -->
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

// watch(searchResult, (result) => {
//   if (!result)
//     return;

//   if (activeDevices.value.length > 0) {
//     messagesSet.value = [];

//     result.events.forEach(event => {
//       messagesSet.value.push(event);
//     });
//     console.log(messagesSet.value)

//     const sortedEventData = messagesSet.value.sort((a, b) => a.timestamp - b.timestamp);
//     console.log(sortedEventData)

//     const rangeData = [];
//     const momentData = [];

//     // Group events by provider name
//     const groups = {};
//     sortedEventData.forEach(event => {
//       const { providerName, timestamp } = event;
//       if (!groups[providerName]) {
//         groups[providerName] = [];
//       }
//       groups[providerName].push(event);
//     });

//     // Create ranges and moments
//     for (const providerName in groups) {
//       const events = groups[providerName];
//       let rangeStart = events[0].timestamp;
//       let rangeEnd = events[0].timestamp;

//       for (let i = 1; i < events.length; i++) {
//         const currentEvent = events[i];
//         const prevEvent = events[i - 1];

//         const timeDiff = currentEvent.timestamp - prevEvent.timestamp;
//         const isWithinHour = timeDiff <= 60 * 60 * 1000; // One hour in milliseconds

//         if (isWithinHour) {
//           rangeEnd = currentEvent.timestamp;
//         } else {
//           rangeData.push({
//             name: providerName,
//             start: rangeStart,
//             end: rangeEnd
//           });
//           momentData.push({
//             x: rangeEnd,
//             y: `${providerName} - Range End`
//           });

//           rangeStart = currentEvent.timestamp;
//           rangeEnd = currentEvent.timestamp;
//         }
//       }

//       // Push the last range
//       rangeData.push({
//         name: providerName,
//         start: rangeStart,
//         end: rangeEnd
//       });
//       momentData.push({
//         x: rangeEnd,
//         y: `${providerName} - Range End`
//       });
//     }

//     // Create chart and series
//     const chart = anychart.timeline();
//     const rangeSeries = chart.range(rangeData);
//     console.log(rangeData)
//     console.log(momentData)
//     // const momentSeries = chart.moment(momentData);

//     // Set the container
//     chart.container(timeline.value);

//     // Draw the chart
//     chart.draw();

//   }
// })

watch(searchResult, (result) => {
  if (!result)
    return;

  if (activeDevices.value.length > 0) {
    const messagesSet = [];
    result.events.forEach(event => {
      messagesSet.push(event);
    });

    const sortedEventData = messagesSet.sort((a, b) => a.timestamp - b.timestamp);

    const rangeData = [];
    const momentData = [];

    // Group events by provider name
    const groups = {};
    sortedEventData.forEach(event => {
      const { providerName, timestamp } = event;
      if (!groups[providerName]) {
        groups[providerName] = [];
      }
      groups[providerName].push(event);
    });

    // Create ranges and moments for each provider
    for (const providerName in groups) {
      const providerEvents = groups[providerName];
      let rangeStart = providerEvents[0].timestamp;
      let rangeEnd = providerEvents[0].timestamp;

      for (let i = 1; i < providerEvents.length; i++) {
        console.log(providerEvents[i].timestamp + " provider event " + providerEvents[i].providerFriendlyName)
        const currentEvent = providerEvents[i];
        const prevEvent = providerEvents[i - 1];

        const timeDiff = currentEvent.timestamp - prevEvent.timestamp;
        const isWithinTwoHours = timeDiff <= 2 * 60 * 60 * 1000; // Two hours in milliseconds

        if (isWithinTwoHours) {
          console.log(isWithinTwoHours)
          rangeEnd = currentEvent.timestamp;
        } else {
          // If events are not within 2 hours, treat them as individual moments
          momentData.push({
            x: prevEvent.timestamp,
            y: `${providerName} - Range End`
          });

          // Start a new range from the current event
          rangeStart = currentEvent.timestamp;
          rangeEnd = currentEvent.timestamp;
        }
      }

      // Push the last range for the provider
      rangeData.push({
        name: providerName,
        start: rangeStart,
        end: rangeEnd
      });

      // Add the last event as a moment
      momentData.push({
        x: rangeEnd,
        y: `${providerName} - Range End`
      });
    }

    // Create chart and series
    const chart = anychart.timeline();
    const rangeSeries = chart.range(rangeData);
    const momentSeries = chart.moment(momentData);
    // console.log(rangeData)
    // console.log(momentData)

    // Set the container
    chart.container(timeline.value);

    // Draw the chart
    chart.draw();
  }
});


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

  // var rangeData1 = [
  //   ["Task 1", Date.UTC(2004, 0, 4), Date.UTC(2004, 11, 1)],
  //   ["Task 2", Date.UTC(2004, 7, 1), Date.UTC(2005, 8, 10)],
  //   ["New Task 1", Date.UTC(2005, 10, 1), Date.UTC(2006, 5, 1)],
  //   ["New Task 2", Date.UTC(2006, 5, 15), Date.UTC(2006, 11, 1)]
  // ];

  // var momentData1 = [
  //   { x: Date.UTC(2004, 2, 21), y: "Meeting 1" },
  //   { x: Date.UTC(2005, 3, 19), y: "Meeting 2" },
  //   { x: Date.UTC(2006, 1, 1), y: "Meeting 3" }
  // ];

  // var momentData2 = [
  //   { x: Date.UTC(2004, 5, 12), y: "Training 1" },
  //   { x: Date.UTC(2005, 5, 1), y: "Training 2" },
  //   { x: Date.UTC(2006, 1, 26), y: "Training 3" }
  // ];

  // // create a chart
  // var chart = anychart.timeline();

  // // create the first range series
  // var rangeSeries1 = chart.range(rangeData1);

  // // create the first moment series
  // var momentSeries1 = chart.moment(momentData1);

  // // create the second moment series
  // var momentSeries2 = chart.moment(momentData2);

  // // set the container id
  // chart.container(timeline.value);

  // // initiate drawing the chart  
  // chart.draw();

});

</script> 

<style scoped>

.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200vh; /* Adjust the height as needed */
}

.timeline-container {
  width: 100%;
  height: 60%;
}

#container {
  width: 90%;
  height: 60%;
  margin: 0;
  padding: 0;
}

#legendContainer {
  margin-top: 20px;
}

.center {
  margin: auto;
  margin-top: 15%;
  width: 30em;
  text-align: center;
}
</style>


