<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { ref, computed, watch, onMounted, render, nextTick } from 'vue';
import * as d3 from 'd3';
import { activeDevices } from '../store.js';
import * as anychart from 'anychart'

const data = ref([
  { x: "A", value: 637166 },
  { x: "B", value: 721630 },
  { x: "C", value: 148662 },
  { x: "D", value: 78662 },
  { x: "E", value: 90000 }
]);

const selectedCar = ref('') 
const cars = ref ([
        { label: 'Volvo', value: 'volvo' },
        { label: 'Saab', value: 'saab' },
        { label: 'Opel', value: 'opel' },
        { label: 'Audi', value: 'audi' },
      ]);

const radius = ref(200);
const pieChart = ref(null);
var showChart = ref(false);
var showDropdown = ref(false);
const selectedFilters = ref([]);
const filters = ref([
  { id: 1, label: 'Filter 1' },
  { id: 2, label: 'Filter 2' },
]);
const dropdownPosition = ref({ top: 0, left: 0 });

const computedActiveDevices = computed(() => {
  return activeDevices.value;
});

watch(() => computedActiveDevices.value.length, () => {
  if (computedActiveDevices.value.length > 0) {
    showChart = true;
    nextTick(() => {
      anyPieChart();
    });
  } else {
    showChart = false;
  }
});

onMounted(() => {
  if (computedActiveDevices.value.length > 0) {
    nextTick(() => {
      anyPieChart();
    });
  }
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
<!-- 
<template>
  <div>
    <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div>
    <div v-else class="page-container">

      <button @click="toggleDropdown">Toggle Dropdown</button>
      <div v-if="showDropdown"  class="dropdown">
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
      </div>

      <div class="chart-container">
        <div ref="pieChart" style="width: 500px; height: 500px;"></div>
      </div>
    </div>
  </div>
</template> -->

<template>
  <div >
    <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div>
    <div v-else class="page-container">
      <!-- <button @click="toggleDropdown">Toggle Dropdown</button>
      <div v-if="showDropdown" class="dropdown">
        <div>Item 1</div>
        <div >Item 2</div>
        <div >Item 3</div>
      </div> -->
      <label for="cars">Choose a car:</label>
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
  top: 100%; /* Position below the button */
  left: 0;
  border: 1px solid #ccc;
  padding: 5px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

</style>