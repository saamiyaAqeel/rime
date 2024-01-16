<!-- <template>
  <div>
    <h2>Pie Chart</h2>
    <svg ref="pieChart" width="500" height="400"></svg>
  </div>
</template>

<script setup>
import * as d3 from 'd3';

const data = [
  { name: "Alex", share: 20.70 },
  { name: "Shelly", share: 30.92 },
  { name: "Clark", share: 15.42 },
  { name: "Matt", share: 13.65 },
  { name: "Jolene", share: 19.31 }
];

const width = 500;
const height = 400;
const radius = 200;

const refs = defineRefs();

const svg = d3.select(refs.pieChart);
const g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

const ordScale = d3.scaleOrdinal()
  .domain(data.map(d => d.name))
  .range(['#ffd384', '#94ebcd', '#fbaccc', '#d3e0ea', '#fa7f72']);

const pie = d3.pie().value(d => d.share);

const arc = g.selectAll("arc")
  .data(pie(data))
  .enter();

const path = d3.arc()
  .outerRadius(radius)
  .innerRadius(0);

arc.append("path")
  .attr("d", path)
  .attr("fill", d => ordScale(d.data.name));

const label = d3.arc()
  .outerRadius(radius)
  .innerRadius(0);

arc.append("text")
  .attr("transform", d => `translate(${label.centroid(d)})`)
  .text(d => d.data.name)
  .style("font-family", "arial")
  .style("font-size", 15);
</script> -->

<!-- <template>
  <div>
    <h2>Pie Chart</h2>
    <svg ref="pieChart" width="500" height="400"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3';

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
      colors: ['#ffd384', '#94ebcd', '#fbaccc', '#d3e0ea', '#fa7f72']
    };
  },
  mounted() {
    this.renderChart();
  },
  methods: {
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
    },
  },
};
</script>

<style scoped>
/* Add your styles here if needed */
</style> -->

<template>
  <div>
    <h2>Pie Chart</h2>
    <svg ref="pieChart" width="500" height="400"></svg>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as d3 from 'd3';

const data = [
  { name: "Alex", share: 20.70 },
  { name: "Shelly", share: 30.92 },
  { name: "Clark", share: 15.42 },
  { name: "Matt", share: 13.65 },
  { name: "Jolene", share: 19.31 }
];

const radius = 200;

const svgRef = ref("pieChart");

onMounted(() => {
  const svg = d3.select(svgRef.value);
  const width = svg.attr("width");
  const height = svg.attr("height");

  const g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

  const ordScale = d3.scaleOrdinal()
    .domain(data.map(d => d.name))
    .range(['#ffd384', '#94ebcd', '#fbaccc', '#d3e0ea', '#fa7f72']);

  const pie = d3.pie().value(d => d.share);

  const arc = g.selectAll("arc")
    .data(pie(data))
    .enter();

  const path = d3.arc()
    .outerRadius(radius)
    .innerRadius(0);

  arc.append("path")
    .attr("d", path)
    .attr("fill", d => ordScale(d.data.name));

  const label = d3.arc()
    .outerRadius(radius)
    .innerRadius(0);

  arc.append("text")
    .attr("transform", d => `translate(${label.centroid(d)})`)
    .text(d => d.data.name)
    .style("font-family", "arial")
    .style("font-size", 15);
});
</script>
