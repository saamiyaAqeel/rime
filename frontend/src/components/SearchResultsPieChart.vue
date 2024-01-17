
<template>
  <div>
    <h2>Pie Chart</h2>
    <div class="chart-container">
      <div>
        <svg ref="pieChart" width="500" height="400"></svg>
      </div>
      <div>
        <svg ref="myDataviz" height="300" width="450"></svg>
      </div>
    </div>
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
         
      var legend = d3.select(this.$refs.myDataviz);

      var keys = this.data.map(d => d.name);

      var color = d3.scaleOrdinal()
        .domain(keys)
        .range(this.colors);

      legend.selectAll("mydots")
        .data(keys)
        .enter()
        .append("circle")
        .attr("cx", 100)
        .attr("cy", (d, i) => 100 + i * 25) 
        .attr("r", 7)
        .style("fill", d => color(d));

      legend.selectAll("mylabels")
        .data(keys)
        .enter()
        .append("text")
        .attr("x", 120)
        .attr("y", (d, i) => 100 + i * 25) 
        .text(d => d)
        .attr("text-anchor", "left")
        .style("alignment-baseline", "middle");

    },
  },
};
</script>

<style scoped>
.chart-container {
  display: flex;
}

.chart-container > div {
  margin-right: 20px; 
}
</style>


 