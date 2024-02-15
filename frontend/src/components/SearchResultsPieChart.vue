<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { ref, computed, watch, onMounted, render, nextTick } from 'vue';
import * as d3 from 'd3';
import { searchResult } from '../eventsdata.js'
import { activeDevices, rawEventsSearchResult, eventsRefetch } from '../store.js';
import * as anychart from 'anychart'
import axios from 'axios';
const endpoint = ref('http://localhost:5000/api/data');

const responseData = ref(null);
const data = ref([
  { x: "A", value: 637166 },
  { x: "B", value: 721630 },
  { x: "C", value: 148662 },
  { x: "D", value: 78662 },
  { x: "E", value: 90000 }
]);
const messagesSet = ref([]);

const selectedCar = ref('')
const cars = ref([
  { label: 'Volvo', value: 'volvo' },
  { label: 'Saab', value: 'saab' },
  { label: 'Opel', value: 'opel' },
  { label: 'Audi', value: 'audi' },
]);
const pieChart = ref(null);
var showChart = ref(false);
var showDropdown = ref(false);

const computedActiveDevices = computed(() => {
  return activeDevices.value;
});

// watch(() => activeDevices.value.length, () => {

//   if (activeDevices.value.length > 0) {

//     nextTick(() => {
//       searchResult.value.events.forEach(event => {
//         messagesSet.value.push(event.text)
//       });
//     });

//     showChart = true;
//     nextTick(() => {
//       anyPieChart();
//     });
//   }
//   else {
//     showChart = false;
//   }

//   if (messagesSet.value) {
//     // console.log(messagesSet.value)
//     //var postRequest = JSON.stringify(messagesSet.value)
//     var array = ["apple", "banana", "orange"];
//     var postRequest = JSON.stringify(array);

//     axios.post('http://localhost:5000/api/messages', postRequest, {
//       headers: {
//         'Content-Type': 'application/json'
//       }
//     })
//       .then(response => {
//         responseData.value = response.data; // Store the response data in responseData
//         // You can do additional processing here if needed
//         console.log(responseData.value);
//       })
//       .catch(error => {
//         console.error(error); // Log any errors
//       });

//   }
// });

watch(() => activeDevices.value.length, () => {
  if (activeDevices.value.length > 0) {
    nextTick(() => {
      searchResult.value.events.forEach(event => {
        messagesSet.value.push(event.text)
      });
      showChart = true;
      anyPieChart();
      // Only send the post request after all data is pushed into messagesSet.value
      if (messagesSet.value.length > 0) {
        var postRequest = JSON.stringify(messagesSet.value[0]);
        console.log(messagesSet.value[0])
        axios.post('http://localhost:5000/api/messages', postRequest, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(response => {
          responseData.value = response.data; // Store the response data in responseData
          // You can do additional processing here if needed
          console.log(responseData.value);
        })
        .catch(error => {
          console.error(error); // Log any errors
        });
      }
    });
  }
  else {
    showChart = false;
  }
});


onMounted(() => {
  if (computedActiveDevices.value.length > 0) {
    nextTick(() => {
      anyPieChart();
    });
  }

  // Make an HTTP GET request using Axios
  axios.get('http://localhost:5000/api/data')
    .then(response => {
      responseData.value = response.data; // Store the response data in responseData
      // You can do additional processing here if needed
    })
    .catch(error => {
      console.error(error); // Log any errors
    });

});

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
}

const handleItemClick = () => {
  showDropdown.value = false;
}

const anyPieChart = () => {
  const chart = anychart.pie(data.value);
  chart.container(pieChart.value);
  chart.data(data.value)
  chart.draw();
}

</script>

<template>
  <div>
    <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div>
    <div v-else class="page-container">
      <label for="cars">Choose a category:</label>
      <select v-model="selectedCar" name="cars" id="cars">
        <option v-for="(car, index) in cars" :key="index" :value="car.value">{{ car.label }}</option>
      </select>
      <div class="chart-container">
        <div ref="pieChart" style="width: 500px; height: 500px;"></div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.container {
  position: relative;
}

.chart-container {
  display: flex;
}

.page-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}


.dropdown-menu {
  position: absolute;
  top: 70;
  left: 130;
  background-color: #fff;
  border: 1px solid #ccc;
  padding: 10px;
  z-index: 1000;
}

.dropdown-menu label {
  display: block;
  margin-bottom: 8px;
}

.center {
  margin: auto;
  margin-top: 15%;
  width: 30em;
  text-align: center;
}

.dropdown {
  position: absolute;
  top: 100%;
  /* Position below the button */
  left: 0;
  border: 1px solid #ccc;
  padding: 5px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
</style>