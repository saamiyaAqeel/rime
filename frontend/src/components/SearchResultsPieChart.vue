
<template>
  <div class="page-container">
    <div class="title-container">
      <h2>Pie Chart</h2>
      <img src="/filtericon.jpg" alt="Filter Icon" class="filter-icon" @click="toggleDropdown" />
      <div v-if="showDropdown" class="dropdown-menu">
        <label v-for="filter in filters" :key="filter.id">
          <input type="checkbox" v-model="selectedFilters" :value="filter.id" />
          {{ filter.label }}
        </label>
      </div>
    </div>
    <div class="chart-container">
      <div>
        <svg ref="pieChart" width="600" height="500"></svg>
      </div>
      <div>
        <svg ref="myDataviz" height="300" width="450"></svg>
      </div>
    </div>
  </div>
</template>
  
<script>
import * as d3 from 'd3';
import { computed } from 'vue';  // Import computed from Vue
import { activeDevices } from '../store.js';


export default {
  data() {
    return {
      data: [
        { name: "Alex", share: 20.70 },
        { name: "Shelly", share: 30.92 },
        { name: "Clark", share: 15.42 },
        { name: "Matt", share: 13.65 },
        { name: "Jolene", share: 19.31 }
      ],
      radius: 200,
      colors: ['#ffd384', '#94ebcd', '#fbaccc', '#d3e0ea', '#fa7f72'],
      showDropdown: false,
      selectedFilters: [],
      filters: [
        { id: 1, label: 'Filter 1' },
        { id: 2, label: 'Filter 2' },
      ],
      dropdownPosition: { top: 0, left: 0 }
    };
  },
  mounted() {
    this.checkDevices();
  },
  methods: {
    checkDevices() {
      const devices = activeDevices.value;
      if (devices.length == 0) {
        const dynamicDiv = document.createElement('div');

        // Set class and text content
        dynamicDiv.className = 'center text-box';
        dynamicDiv.textContent = "No active devices, please select one to proceed";

        // Append the new div to the page
        this.$el.appendChild(dynamicDiv);

      }
      else {
        this.renderChart
      }
    },
    renderChart() {
      const svg = d3.select(this.$refs.pieChart),
        width = svg.attr("width"),
        height = svg.attr("height"),
        g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

      const ordScale = d3.scaleOrdinal().domain(this.data.map(d => d.name)).range(this.colors);

      const pie = d3.pie().value(d => d.share);

      const arc = g.selectAll("arc")
        .data(pie(this.data))
        .enter();

      const path = d3.arc()
        .outerRadius(this.radius)
        .innerRadius(0);

      arc.append("path")
        .attr("d", path)
        .attr("fill", d => ordScale(d.data.name));

      const label = d3.arc()
        .outerRadius(this.radius)
        .innerRadius(0);

      arc.append("text")
        .attr("transform", d => `translate(${label.centroid(d)})`)
        .text(d => d.data.name)
        .style("font-family", "arial")
        .style("font-size", 15);

      var legend = d3.select(this.$refs.myDataviz);

      var keys = this.data.map(d => d.name);

      var color = d3.scaleOrdinal()
        .domain(keys)
        .range(this.colors);

      legend.selectAll("mysquares")
        .data(keys)
        .enter()
        .append("rect") // Change from "circle" to "rect" to create rectangles
        .attr("x", 100)
        .attr("y", (d, i) => 100 + i * 25)
        .attr("width", 20) // Set the width of the rectangles
        .attr("height", 20) // Set the height of the rectangles
        .style("fill", d => color(d));


      legend.selectAll("mylabels")
        .data(keys)
        .enter()
        .append("text")
        .attr("x", 140)
        .attr("y", (d, i) => 110 + i * 25)
        .text(d => d)
        .attr("text-anchor", "left")
        .style("alignment-baseline", "middle");
    },
    toggleDropdown() {
      const dropdownMenu = this.$refs.dropdownMenu;
      const filterIcon = this.$refs.filterIcon;

      if (filterIcon && dropdownMenu) {
        const iconRect = filterIcon.getBoundingClientRect();
        this.dropdownPosition = {
          top: iconRect.bottom + window.scrollY,
          left: iconRect.left + window.scrollX,
        };
      }

      this.showDropdown = !this.showDropdown;
    }
  },
};
</script>

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