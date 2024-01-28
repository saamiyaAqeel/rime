
<template>
  <div class="timeline-container">
    <div :id="containerId"></div>
    <div id="legendContainer"></div>
  </div>
</template>

<script>
import * as anychart from 'anychart';

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
            var series;

            for (var i = 0; i < data.Timeline.length; i++) {
              series = chart.range([
                [
                  data.Timeline[i].title,
                  data.Timeline[i].start,
                  data.Timeline[i].end,
                ],
              ]);

              // Customize the series if needed
              series.normal().fill(this.getColorByTitle(data.Timeline[i].title));
              series.hovered().fill(this.getColorByTitle(data.Timeline[i].title));
              series.selected().fill(this.getColorByTitle(data.Timeline[i].title));
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

            this.createLegend(data.Timeline, chart);
          }
        );
      });
    });
  },
  methods: {
    createLegend(timelineData, chart) {
      // Get the legend container
      var legendContainer = document.getElementById('legendContainer');

      // Iterate over the timeline data to create legend items
      for (var i = 0; i < timelineData.length; i++) {
        var legendItem = document.createElement('div');
        legendItem.innerHTML = timelineData[i].title;
        legendItem.style.color = chart.getSeriesAt(i).color;

        // Append the legend item to the legend container
        legendContainer.appendChild(legendItem);
      }
    },
    getColorByTitle(title) {
      if (title.includes("A")) {
        return "#ff0000"; // Red for titles containing "A"
      } else if (title.includes("B")) {
        return "#00ff00"; // Green for titles containing "B"
      } else if (title.includes("C")) {
        return "#0000ff"; // Blue for titles containing "C"
      } else {
        return "#808080"; // Default color for other titles
      }
    }
  },
};
</script>


<style scoped>
.timeline-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

#container {
  width: 90%;
  height: 60%;
  margin: 0;
  padding: 0;
}

#legendContainer {
  margin-top: 20px;
}
</style>
