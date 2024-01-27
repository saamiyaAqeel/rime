
<template>
  <div class="timeline-container">
    <div :id="containerId"></div>
  </div>
</template>

<script>
import * as anychart from 'anychart'

export default {
  data() {
    return {
      containerId: 'container',
    };
  },
  mounted() {
    this.$nextTick(() => {
      anychart.onDocumentReady(() => {
        anychart.data.loadJsonFile(
          '/timeline.json',
          (data) => {
            var chart = anychart.timeline();

            for (var i = 0; i < data.Timeline.length; i++) {
              var series = chart.range([
                [
                  data.Timeline[i].title,
                  data.Timeline[i].start,
                  data.Timeline[i].end,
                ],
              ]);
            }

            // Create dataset for the top datapoints
            var pfizerDataSet = anychart.data.set(data.ImportantEvents);

            // Map the top datapoints
            var pfizerMapping = pfizerDataSet.mapAs({
              x: 'date',
              value: 'title',
            });

            // Create top series with moments
            var pfizerMappingSeries = chart.moment(pfizerMapping);

            // Create dataset for the bottom datapoints
            var otherVaccinesDataset = anychart.data.set(data.SecondaryFacts);

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
            chart.title('Timeline of Events');

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
.timeline-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; 
}

#container {
  width: 90%;
  height: 90%;
  margin: 0;
  padding: 0;
}
</style>
