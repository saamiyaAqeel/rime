<script>
export default {
  inheritAttrs: false,
};
</script>

<script setup>
import { ref, watch, onMounted } from "vue";
import { searchResult } from "../eventsdata.js";
import { activeDevices } from "../store.js";
import * as anychart from "anychart";
import axios from "axios";

const relatedWords = ref(false);
const showInfoBox = ref(false);
const noResults = ref(false);
const searchQuery = ref("");
const responseData = ref(null);
const isOpen = ref(false);
var pieChartShow = ref(false);
const selectedOption = ref("Select an option");
const options = [
  "Of Evidenciary Interest",
  "Potential Conversation of Argumentative Nature",
  "Strict Keyword Search",
  "Related-Words Keyword Search",
];

const navigate = () => {
  window.open('https://forms.office.com/Pages/ResponsePage.aspx?id=7qe9Z4D970GskTWEGCkKHt13h9QfEU1Fr6JL1ThahOxUMUdURDhIVFZCMjBMU0VNN1BOWUhLWTIxRS4u', '_blank');
};


const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const selectOption = (option) => {
  selectedOption.value = option;
  isOpen.value = false;
};

const pieChartData = ref([]);
const messagesSet = ref([]);
const pieChart = ref(null);
const tagCloud = ref(null);

watch(selectedOption, (option) => {
  const result = searchResult.value;
  messagesSet.value = [];
  pieChartData.value = [];
  pieChartShow.value = false;

  result.events.forEach((event) => {
    messagesSet.value.push(event.text);
  });

  const formData = new FormData();
  const chunkSize = 10000;

  for (let i = 0; i < messagesSet.value.length; i += chunkSize) {
    const chunk = messagesSet.value.slice(i, i + chunkSize);
    formData.append("data", chunk);
  }

  pieChartData.value = [];
  if (option == "Of Evidenciary Interest") {
    axios
      .post("http://localhost:5000/api/messages", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        responseData.value = response.data;
        const length = responseData.value.arrayLength;
        const chartData = responseData.value.chart_data;
        const text = responseData.value.text;
        console.log(text)
        const xValue = chartData["x"];
        const valuePie = chartData["value"];
        anyPieChart(xValue, valuePie, length);

        const data = [];
        text.forEach((synonym, index) => {
          const value = Math.floor(Math.random() * (70 - 40 + 1)) + 40;
          data.push({ x: synonym, value: value });
        });
        tagCloudDraw(data);

      })
      .catch((error) => {
        console.error(error);
      });
  } else if (option == "Potential Conversation of Argumentative Nature") {
    axios
      .post("http://localhost:5000/api/argumentativeClassifier", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        responseData.value = response.data;
        const length = responseData.value.arrayLength;
        const chartData = responseData.value.chart_data;
        const text = responseData.value.text;
        const xValue = chartData["x"];
        const valuePie = chartData["value"];
        console.log(text)
        anyPieChart(xValue, valuePie, length);

        const data = [];
        text.forEach((synonym, index) => {
          const value = 40
          data.push({ x: synonym, value: value });
        });
        tagCloudDraw(data);

      })
      .catch((error) => {
        console.error(error);
      });
  } else if (option == "Strict Keyword Search") {
    pieChart.value.innerHTML = "";
  } else {
    pieChart.value.innerHTML = "";
  }
});

watch(searchResult, (result) => {
  if (!result) return;

  if (activeDevices.value.length > 0) {
    messagesSet.value = [];
    pieChartData.value = [];
    pieChartShow.value = false;

    result.events.forEach((event) => {
      messagesSet.value.push(event.text);
    });

    const formData = new FormData();
    const chunkSize = 10000;

    for (let i = 0; i < messagesSet.value.length; i += chunkSize) {
      const chunk = messagesSet.value.slice(i, i + chunkSize);
      formData.append("data", chunk);
    }

    var option = selectedOption.value;
    pieChartData.value = [];

    if (option == "Of Evidenciary Interest") {
      axios
        .post("http://localhost:5000/api/messages", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then((response) => {
          responseData.value = response.data;
          const length = responseData.value.arrayLength;
          const chartData = responseData.value.chart_data;
          const text = responseData.value.text;
          const xValue = chartData["x"];
          const valuePie = chartData["value"];
          console.log(text)
          anyPieChart(xValue, valuePie, length);

          const data = [];
          text.forEach((synonym, index) => {
            const value = Math.floor(Math.random() * (70 - 40 + 1)) + 40;
            data.push({ x: synonym, value: value });
          });
          tagCloudDraw(data);
        })
        .catch((error) => {
          console.error(error);
        });
    } else if (option == "Potential Conversation of Argumentative Nature") {
      axios
        .post("http://localhost:5000/api/argumentativeClassifier", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then((response) => {
          responseData.value = response.data;
          const length = responseData.value.arrayLength;
          const chartData = responseData.value.chart_data;
          const text = responseData.value.text;
          const xValue = chartData["x"];
          const valuePie = chartData["value"];
          console.log(text)
          anyPieChart(xValue, valuePie, length);

          const data = [];
          text.forEach((synonym, index) => {
            const value = Math.floor(Math.random() * (70 - 40 + 1)) + 40;
            data.push({ x: synonym, value: value });
          });
          tagCloudDraw(data);
        })
        .catch((error) => {
          console.error(error);
        });
    } else if (option == "Strict Keyword Search") {
      handleSearch();
    } else {
      handleSearch();
    }
  }
});

const anyPieChart = (label, significantValue, length) => {
  pieChart.value.innerHTML = "";

  const chartData = [
    { x: label, value: significantValue },
    { x: "Negligible Value", value: length - significantValue },
  ];

  const chart = anychart.pie(chartData);
  chart.legend().itemsFormatter(function (items) {
    return items.filter((item) => item.text !== "Negligible Value");
  });

  chart.selected().explode("3%");

  chart.select([0]);

  chart.labels().format(function () {
    if (this.index === 1) {
      return "";
    } else {
      if (selectedOption.value == 'Strict Keyword Search' || selectedOption.value == 'Related-Words Keyword Search') {
        return (significantValue / length * 100).toFixed(2) + "%";
      }
      return Math.round(significantValue / length * 100) + "%";
    }
  });

  chart.container(pieChart.value);
  chart.draw();
};

onMounted(() => { });

const tagCloudDraw = (data) => {
  tagCloud.value.innerHTML = "";
  const chart = anychart.tagCloud(data);
  chart.angles([0]);
  chart.tooltip().enabled(false);
  chart.container(tagCloud.value);
  chart.draw();
};

const handleSearch = () => {
  const formData = new FormData();
  const chunkSize = 10000;
  pieChartData.value = [];
  pieChartShow.value = false;

  formData.append("keyword", searchQuery.value);

  for (let i = 0; i < messagesSet.value.length; i += chunkSize) {
    const chunk = messagesSet.value.slice(i, i + chunkSize);
    formData.append("data", chunk);
  }

  if (searchQuery.value) {
    if (selectedOption.value == "Strict Keyword Search") {
      axios
        .post("http://localhost:5000/api/strictKeyword", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then((response) => {
          responseData.value = response.data;
          const length = responseData.value.arrayLength;
          const chartData = responseData.value.chart_data;
          console.log(responseData.value)
          const xValue = chartData["x"];
          const valuePie = chartData["value"];
          console.log(xValue)
          console.log(valuePie)
          if (valuePie == "0.0") {
            console.log("show no words found message");
            noResults.value = true;
          } else {
            noResults.value = false;
            responseData.value = response.data;
            const xValue = chartData["x"];
            const valuePie = chartData["value"];
            anyPieChart(xValue, valuePie, length);
          }
        })
        .catch((error) => {
          console.error(error);
        });
    } else {
      axios
        .post("http://localhost:5000/api/relatedKeyword", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then((response) => {
          responseData.value = response.data;
          const length = responseData.value.arrayLength
          const synonyms = responseData.value.synonyms;
          const chartData = responseData.value.chart_data;
          const xValue = chartData["x"];
          const valuePie = chartData["value"];
          if (valuePie == "0.0") {
            console.log("show no words found message");
            noResults.value = true;
          } else {
            noResults.value = false;
            responseData.value = response.data;
            anyPieChart(xValue, valuePie, length);

            const data = [];
            synonyms.forEach((synonym, index) => {
              const value = Math.floor(Math.random() * (70 - 40 + 1)) + 40;
              data.push({ x: synonym, value: value });
            });
            tagCloudDraw(data);
          }
        })
        .catch((error) => {
          console.error(error);
        });
    }
  }
};
</script>

<template>
  <div>
    <button id="navigateButton" @click="navigate" class="button-space">Send Feedback</button>
    <div v-if="activeDevices.length === 0" class="center text-box">
      Select one or more devices at the top left to begin.
    </div>
    <div v-else class="page-container">
      <div class="dropdown">
        <button @click="toggleDropdown" class="dropdown-toggle">
          {{ selectedOption }}
        </button>
        <div v-if="isOpen" class="dropdown-menu">
          <ul>
            <li v-for="(option, index) in options" :key="index" @click="selectOption(option)" class="dropdown-item">
              {{ option }}
            </li>
          </ul>
        </div>
        <div class="info-icon" @mouseover="showInfoBox = true" @mouseleave="showInfoBox = false">
          <span class="icon">?</span>
          <div v-if="selectedOption === 'Select an option'" class="info-box" v-show="showInfoBox">
            The pie chart page displays the contents of the dataset in a multitude of ways,
            you can check the potential contents of the data and search for specific and related words.
          </div>
          <div v-if="selectedOption === 'Of Evidenciary Interest'" class="info-box" v-show="showInfoBox">
            The pie chart page displays the percentage of the dataset that can flag up when it comes to evidenciary
            interest,
            for example criminal activities, it should be known that the results are produced using a classfier which
            will not always be accurate.
          </div>
          <div v-if="selectedOption === 'Potential Conversation of Argumentative Nature'" class="info-box"
            v-show="showInfoBox">
            The pie chart page displays the percentage of the dataset that can flag up when it comes to potential
            argumentaive nature between individuals.
            It should be known that the results are produced using a classfier which will not always be accurate.
          </div>
          <div v-if="selectedOption === 'Strict Keyword Search'" class="info-box"
            v-show="showInfoBox">
            This pie chart will show you the percentage of a certain word that is searched throughout the dataset such as the word "hello" or "meet". if the word is not found
            , a message will be shown
          </div>
          <div v-if="selectedOption === 'Related-Words Keyword Search'" class="info-box"
            v-show="showInfoBox">
           This pie chart will show you the percentage of the words that was searched along side the words that are related to that word, 
           the tag cloud next to it displays the words related to searched word.
          </div>
        </div>
      </div>

      <div v-if="selectedOption === 'Strict Keyword Search' ||
      selectedOption === 'Related-Words Keyword Search'
      " class="search-box">
        <input type="text" v-model="searchQuery" placeholder="Enter search query" />
        <button @click="handleSearch">Search</button>
      </div>

      <div class="chart-container">
        <div v-if="noResults === true" class="center text-box">
          No matching word found in search results
        </div>
      </div>

      <div class="chart-container">
        <div v-if="selectedOption" ref="pieChart" style="width: 500px; height: 500px"></div>
        <div
          v-if="selectedOption === 'Related-Words Keyword Search' || selectedOption === 'Of Evidenciary Interest' || selectedOption === 'Potential Conversation of Argumentative Nature'"
          ref="tagCloud" style="width: 600px; height: 600px"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.button-space {
  margin-top: 20px;
  margin-left: 10px;
}

.info-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.info-icon {
  position: relative;
  display: inline-block;
  margin-right: 10px;
  margin-left: 10px
}

.info-icon:hover .info-box {
  display: block;
}

.icon {
  display: inline-block;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ccc;
  color: #fff;
  text-align: center;
  line-height: 40px;
  cursor: pointer;
  margin-right: 20px;
}


.info-box {
  position: absolute;
  width: 500px;  
  bottom: 100%;  
  left: 50%;    
  transform: translate(-50%, -10px); 
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: none; 
  z-index: 1000; 
}


.tag-cloud-container {
  flex: 0 0 50%;
  padding-left: 20px;
}

.center {
  margin: auto;
  margin-top: 15%;
  width: 30em;
  text-align: center;
}

.dropdown {
  position: relative;
  display: inline-block;
  min-width: fit-content;
  margin-right: 20px;
}

.dropdown-toggle {
  background-color: #f0f0f0;
  border: none;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.dropdown-item {
  padding: 10px;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f0f0f0;
}

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

.search-box {
  margin-top: 20px;
  display: flex;
  align-items: center;
}

.search-box input {
  padding: 5px;
  margin-right: 10px;
}

.search-box button {
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
