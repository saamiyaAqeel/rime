<!-- 
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
        legendItem.style.display = 'flex'; // Set display to flex for horizontal alignment

        // Create a colored square
        var square = document.createElement('div');
        square.style.width = '20px'; // Adjust as needed
        square.style.height = '20px'; // Adjust as needed
        square.style.backgroundColor =  this.getColorByTitle(timelineData[i].title) ;
        square.style.marginRight = '5px'; // Adjust as needed

        // Create the label
        var label = document.createElement('div');
        label.innerHTML = timelineData[i].title;

        // Append both the square and label to the legend item
        legendItem.appendChild(square);
        legendItem.appendChild(label);

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
</script> -->

 <!-- <style scoped>
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
</style>  -->
























<template>
  <div class="timeline-container">
    <div ref="timeline"></div>                          
    <div id="legendContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as anychart from 'anychart';

const containerId = 'container';
const timeline = ref(null);

const getColorByTitle = (title) => {
  if (title.includes('A')) {
    return '#ff0000';
  } else if (title.includes('B')) {
    return '#00ff00';
  } else if (title.includes('C')) {
    return '#0000ff';
  } else {
    return '#808080';
  }
};

const createLegend = (timelineData, chart) => {
  const legendContainer = document.getElementById('legendContainer');

  for (let i = 0; i < timelineData.length; i++) {
    const legendItem = document.createElement('div');
    legendItem.style.display = 'flex';

    const square = document.createElement('div');
    square.style.width = '20px';
    square.style.height = '20px';
    square.style.backgroundColor = getColorByTitle(timelineData[i].title);
    square.style.marginRight = '5px';

    const label = document.createElement('div');
    label.innerHTML = timelineData[i].title;

    legendItem.appendChild(square);
    legendItem.appendChild(label);

    legendContainer.appendChild(legendItem);
  }
};

onMounted(() => {
  // anychart.onDocumentReady(() => {
    // anychart.data.loadJsonFile('/timeline.json', (data) => {
    //   const chart = anychart.timeline();
    //   let series;

    //   for (let i = 0; i < data.Timeline.length; i++) {
    //     series = chart.range([
    //       [
    //         data.Timeline[i].title,
    //         data.Timeline[i].start,
    //         data.Timeline[i].end,
    //       ],
    //     ]);

    //     series.normal().fill(getColorByTitle(data.Timeline[i].title));
    //     series.hovered().fill(getColorByTitle(data.Timeline[i].title));
    //     series.selected().fill(getColorByTitle(data.Timeline[i].title));
    //   }

      // const pfizerDataSet = anychart.data.set(data.ImportantEvents);
      // const pfizerMapping = pfizerDataSet.mapAs({
      //   x: 'date',
      //   value: 'title',
      // });
      // const pfizerMappingSeries = chart.moment(pfizerMapping);

      // const otherVaccinesDataset = anychart.data.set(data.SecondaryFacts);
      // const otherVaccinesDatasetMapping = otherVaccinesDataset.mapAs({
      //   x: 'date',
      //   value: 'title',
      // });
      // const otherVaccinesSeries = chart.moment(otherVaccinesDatasetMapping);

    //   chart.scale().zoomLevels([{ unit: 'month', count: 1 }]);
    //   chart.axis().height(60);
    //   chart.axis().labels().format(function () {
    //     return anychart.format.dateTime(this.tickValue, 'MMM yyyy');
    //   });
    //   chart.scroller().enabled(true);
    //   chart.title('Timeline of Events');
    //   chart.container(timeline.value);
    //   chart.draw();

    //   createLegend(data.Timeline, chart);
    // });
  // });

  // var rangeData1 = [
  //   ["Task 1", Date.UTC(2004, 0, 4), Date.UTC(2004, 7, 1)],
  //   ["Task 2", Date.UTC(2004, 7, 1), Date.UTC(2005, 8, 10)]
  // ];

  // var rangeData2 = [
  //   ["New Task 1", Date.UTC(2005, 10, 1), Date.UTC(2006, 5, 1)],
  //   ["New Task 2", Date.UTC(2006, 5, 15), Date.UTC(2006, 11, 1)]
  // ];

  // var momentData1 = [
  //   [Date.UTC(2004, 2, 21), "Meeting 1"],
  //   [Date.UTC(2005, 3, 19), "Meeting 2"],
  //   [Date.UTC(2006, 1, 1), "Meeting 3"]
  // ];

  // var momentData2 = [
  //   [Date.UTC(2004, 5, 12), "Training 1"],
  //   [Date.UTC(2005, 5, 1), "Training 2"],
  //   [Date.UTC(2006, 1, 26), "Training 3"]
  // ];

  var chart = anychart.timeline();

  anychart.data.loadJsonFile('/timeline.json', (data) => {
    let series;

    for (let i = 0; i < data.Timeline.length; i++) {
      series = chart.range([
        [
          data.Timeline[i].title,
          data.Timeline[i].start,
          data.Timeline[i].end,
        ],
      ]);

      series.normal().fill(getColorByTitle(data.Timeline[i].title));
      series.hovered().fill(getColorByTitle(data.Timeline[i].title));
      series.selected().fill(getColorByTitle(data.Timeline[i].title));
    }
  });

  chart.container(timeline.value);
  // chart.scale().zoomLevels([{ unit: 'month', count: 1 }]);
  chart.axis().height(100);
  // chart.axis().labels().format(function () {
  //   return anychart.format.dateTime(this.tickValue, 'MMM yyyy');
  // });
  chart.scroller().enabled(true);
  chart.title('Timeline of Events');
  chart.draw();

});

</script> 

<style scoped>
.timeline-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 600vh;
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


