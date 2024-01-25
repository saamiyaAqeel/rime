
<template>
  <div>
    <div :id="containerId"></div>
  </div>
</template>

<script>
import * as anychart from 'anychart'

export default {
  data() {
    return {
      containerId: 'container', // Set the container ID
    };
  },
  mounted() {
    this.$nextTick(() => {
      // Load JSON file and create AnyChart timeline
      anychart.onDocumentReady(() => {
        anychart.data.loadJsonFile(
          '/timeline.json',
          (data) => {
            // Create timeline chart
            var chart = anychart.timeline();

            // Create the main timeline datapoints
            for (var i = 0; i < data.pfizerTimeline.length; i++) {
              // Create range series
              var series = chart.range([
                [
                  data.pfizerTimeline[i].title,
                  data.pfizerTimeline[i].start,
                  data.pfizerTimeline[i].end,
                ],
              ]);
            }

            // Create dataset for the top datapoints
            var pfizerDataSet = anychart.data.set(data.pfizerFacts);

            // Map the top datapoints
            var pfizerMapping = pfizerDataSet.mapAs({
              x: 'date',
              value: 'title',
            });

            // Create top series with moments
            var pfizerMappingSeries = chart.moment(pfizerMapping);

            // Create dataset for the bottom datapoints
            var otherVaccinesDataset = anychart.data.set(data.otherVaccines);

            // Map the bottom dataset
            var otherVaccinesDatasetMapping = otherVaccinesDataset.mapAs({
              x: 'date',
              value: 'title',
            });

            // Create bottom series with moments
            var otherVaccinesSeries = chart.moment(otherVaccinesDatasetMapping);

            // Set chart scale levels
            chart.scale().zoomLevels([
              [
                { unit: 'month', count: 1 }
              ]
            ]);

            // Enable chart scroller
            chart.scroller().enabled(true);

            // Set chart's title
            chart.title('Timeline OF Events');

            // Set container id for the chart
            chart.container(this.containerId);

            // Initiate chart drawing
            chart.draw();
          }
        );
      });
    });
  },
};
</script>

<style scoped>

#container {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

</style>
