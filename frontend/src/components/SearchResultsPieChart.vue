<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { searchResult } from '../eventsdata.js'
import { activeDevices } from '../store.js';
import * as anychart from 'anychart'
import axios from 'axios';

const responseData = ref(null);
const isOpen = ref(false);
const selectedOption = ref('Select an option');
const options = ['Option 1', 'Option 2', 'Option 3'];

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const selectOption = (option) => {
  selectedOption.value = option;
  isOpen.value = false;
};

const pieChartData = ref([])
const messagesSet = ref([]);
const pieChart = ref(null);

watch(searchResult, (result) => {
  if (!result)
    return;

  if (activeDevices.value.length > 0) {
    messagesSet.value = [];
    pieChartData.value = [];

    result.events.forEach(event => {
      messagesSet.value.push(event.text);
    });
    console.log(messagesSet.value)

    const formData = new FormData();
    const chunkSize = 10000;

    for (let i = 0; i < messagesSet.value.length; i += chunkSize) {
      const chunk = messagesSet.value.slice(i, i + chunkSize);
      formData.append('data', chunk);
    }

    axios.post('http://localhost:5000/api/messages', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
      .then(response => {
        responseData.value = response.data;
        console.log(responseData.value)

        const xValue = responseData.value["x"];
        const valuePie = responseData.value["value"];
        pieChartData.value.push({ x: xValue, value: valuePie });
        const otherEntry = 100 - parseInt(valuePie);
        pieChartData.value.push({ x: "", value: otherEntry });
        anyPieChart(pieChartData.value);

      })
      .catch(error => {
        console.error(error);
      });
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

      <div class="dropdown">
        <button @click="toggleDropdown" class="dropdown-toggle">{{ selectedOption }}</button>
        <div v-if="isOpen" class="dropdown-menu">
          <ul>
            <li v-for="(option, index) in options" :key="index" @click="selectOption(option)" class="dropdown-item">{{
              option }}</li>
          </ul>
        </div>
      </div>

      <div class="chart-container">
        <div ref="pieChart" style="width: 500px; height: 500px;"></div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.center {
  margin: auto;
  margin-top: 15%;
  width: 30em;
  text-align: center;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  background-color: #f0f0f0;
  border: none;
  padding: 10px;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.dropdown-item {
  padding: 10px;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f0f0f0;
}

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

</style>