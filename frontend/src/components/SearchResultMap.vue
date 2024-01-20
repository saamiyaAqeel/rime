
 <template>
    <div ref="mapDiv"></div>
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
  
        // new maps.Map(document.getElementById('map'), {
        new maps.Map(this.$refs.mapDiv, {
          center: { lat: 61.180059, lng: -149.822075 },
          scrollwheel: false,
          zoom: 4
        });
      }
    }
  };
  </script>
  