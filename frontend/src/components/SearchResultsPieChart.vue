<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { ref, computed, watch, onMounted, render, nextTick } from 'vue';
import * as d3 from 'd3';
import { searchResult } from '../eventsdata.js'
import { activeDevices, rawEventsSearchResult, eventsRefetch, eventsSearchResultById, devices } from '../store.js';
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
const pieChartData = ref([])
const messagesSet = ref([]);
var showChartPie = 1
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

watch(searchResult, (result) => {
  if (!result)
    return;

  if (activeDevices.value.length > 0) {
    // Clear existing messages and chart data
    messagesSet.value = [];
    pieChartData.value = [];

    // Fetch messages for active devices
    result.events.forEach(event => {
      messagesSet.value.push(event.text);
    });
    console.log(messagesSet.value)

    // Construct request payload
    const discussion = [
      "Debating the ethics of copyright law",
      "Analyzing the impact of tax evasion on society",
      "Discussing the legalization of marijuana",
      "Debating the ethics of surveillance in public spaces",
      "Analyzing the consequences of human trafficking"
    ];

    const postRequest = JSON.stringify(discussion);

    // Send request to API
    axios.post('http://localhost:5000/api/messages', postRequest, {
      headers: {
        'Content-Type': 'application/json'
      },
    })
      .then(response => {
        responseData.value = response.data;

        // Process response data and update pie chart data
        const xValue = responseData.value["x"];
        const valuePie = responseData.value["value"];
        pieChartData.value.push({ x: xValue, value: valuePie });
        const otherEntry = 100 - parseInt(valuePie);
        pieChartData.value.push({ x: "", value: otherEntry });

        // Draw pie chart
        anyPieChart(pieChartData.value);
        showChartPie = 0;
      })
      .catch(error => {
        console.error(error);
      });
  } else {
    showChartPie = 1;
  }

});

onMounted(() => {
});

const anyPieChart = (chartData) => {
  const chart = anychart.pie(chartData);
  chart.container(pieChart.value);
  chart.data(chartData);
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
      <div v-if="showChartPie === 0" class="chart-container">
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