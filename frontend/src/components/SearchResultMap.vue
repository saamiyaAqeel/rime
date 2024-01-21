
   <template>
    <div ref="mapDiv" style="height: calc(100vh - 20px); width: calc(50% - 20px); float: left; margin: 30px; border: 4px solid #0e0e0e;"></div>
  </template>
  
  <script>
  import { loadedGoogleMapsAPI } from '../main.js';
  
  export default {
    name: 'MapEl',
    mounted() {
      loadedGoogleMapsAPI.then(() => {
        this.initMap();
      });
    },
    methods: {
      initMap() {
        // Access the google.maps object through the callback
        const maps = google.maps;
  
        const center = new maps.LatLng(52.9548, -1.1581);
  
        const mainMap = new maps.Map(this.$refs.mapDiv, {
          center: center,
          scrollwheel: false,
          zoom: 12 
        });
  
        const marker = new maps.Marker({
          position: center,
          map: mainMap,
          title: 'Nottingham Marker'
        });
      }
    }
  };
  </script>
  