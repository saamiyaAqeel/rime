
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

            var pfizerDataSet = anychart.data.set(data.ImportantEvents);

            var pfizerMapping = pfizerDataSet.mapAs({
              x: 'date',
              value: 'title',
            });

            var pfizerMappingSeries = chart.moment(pfizerMapping);

            var otherVaccinesDataset = anychart.data.set(data.SecondaryFacts);

            var otherVaccinesDatasetMapping = otherVaccinesDataset.mapAs({
              x: 'date',
              value: 'title',
            });

            var otherVaccinesSeries = chart.moment(otherVaccinesDatasetMapping);

            chart.scale().zoomLevels([
              [
                { unit: 'month', count: 1 }
              ]
            ]);

            chart.axis().height(60);
            chart.axis().labels().format(function () {
              return anychart.format.dateTime(this.tickValue, 'MMM yyyy');
            });
            
            chart.scroller().enabled(true);
            chart.title('Timeline of Events');
            chart.container(this.containerId);
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
