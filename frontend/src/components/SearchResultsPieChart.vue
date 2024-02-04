<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { ref, computed, watch, onMounted, render , nextTick } from 'vue';
import * as d3 from 'd3';
import { activeDevices } from '../store.js';
import * as anychart from 'anychart'


// Reactive state using ref
const data = ref([
  { x: "A", value: 637166 },
  { x: "B", value: 721630 },
  { x: "C", value: 148662 },
  { x: "D", value: 78662 },
  { x: "E", value: 90000 }
]);

const radius = ref(200);
//const pieChart = ref(null)
//defineProps(['pieChart'])
const pieChart = ref(null);
var showChart = ref(false);
const colors = ref(['#ffd384', '#94ebcd', '#fbaccc', '#d3e0ea', '#fa7f72']);
const showDropdown = ref(false);
const selectedFilters = ref([]);
const filters = ref([
  { id: 1, label: 'Filter 1' },
  { id: 2, label: 'Filter 2' },
]);
const dropdownPosition = ref({ top: 0, left: 0 });

// Computed property
// const computedActiveDevices = computed(() => {
//   return activeDevices.value;
// });

// watch(() => activeDevices.value.length, () => {
//   if (activeDevices.value.length > 0) {
//     console.log("hello hello im watching u");
//     //anyPieChart();
//     showChart = true;
//   }
//   else {
//     showChart = false
//   }
//   // checkDevices();
// });


// // Lifecycle hook
// onMounted(() => {
//   // console.log(activeDevices.value.length)
//   // if (activeDevices.value.length > 0) {
//   //   nextTick();

//   // if (activeDevices.value.length > 0) {
//   //   anyPieChart();
//   // }
  
//       anyPieChart();
//  // anyPieChart();
//   //}
// });

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
      <div class="chart-container">
        <div ref="pieChart" style="width: 500px; height: 500px;"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

.title-container {
  display: flex;
  align-items: center;
}

.filter-icon {
  width: 40px;
  /* Set the desired width */
  height: 40px;
  /* Set the desired height */
  margin-left: 10px;
  /* Adjust the margin as needed */
  cursor: pointer;
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
</style>