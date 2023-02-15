<template>
  <div class="main-container">
    <div id="loading-screen-wrapper">

    </div>
    <div class="text-body-1 text-medium-emphasis">
      <transition-group name="fade">
        <div class="LoadingText" v-if="showLoadingText">
          <div>
            {{ curLoadingText }}
          </div>
        </div>
      </transition-group>
    </div>
    <div>
      <div class="logo-container">
        <transition name="scale">
          <v-img v-if="true" max-height="40" class="UcodeLogo" src="UCODE_Logo_black.png"></v-img>
        </transition>
      </div>
    </div>
  </div>

</template>

<script lang="ts" setup>
import { ref, onMounted, watch, reactive } from 'vue';
import Globe from 'globe.gl';
import * as THREE from 'three'
import { useStore } from "vuex";
import type { AOIState } from '@/store/modules/AOIState';


const store = useStore();

let globedData = reactive([{ name: '', lat: null, lon: null }])
const width = window.innerWidth
const height = window.innerHeight
let world = ref<any>(null)
onMounted(() => {
  world = Globe({ animateIn: false })

    .globeImageUrl('earth-day.jpg')
    .backgroundColor('#7FA8B5')
    .width(width)
    .height(height)
    .objectLat('lat')
    .objectLng('lon')
    .objectAltitude(0)
    .labelLat('lat')
    .labelLng('lon')
    .labelDotRadius(0)
    .labelColor(() => 'rgba(0, 0, 0, 1)')
    .labelDotOrientation(() => 'bottom')
    .labelText('name')
    .labelSize(3)
    .labelResolution(2)
    .atmosphereColor('lightgoldenrodyellow')

    (document.getElementById('loading-screen-wrapper'))

    const geo = new THREE.OctahedronGeometry(1.6,2)
    const material = new THREE.MeshBasicMaterial( {color: 0x000000} );
    world.objectThreeObject(() => new THREE.Mesh(geo, material));


  window.addEventListener('resize', (event) => {
    world.width(event.target?.innerWidth)
    world.height(event.target?.innerHeight)
  });

})

watch(store.state.aoi, function(state: AOIState) {
  if (state.projectSpecification != null && globedData[0].name =='') {
    globedData[0].name = state.projectSpecification.project_name
    globedData[0].lat = state.projectSpecification.bbox.ymax
    globedData[0].lon = state.projectSpecification.bbox.xmax
    world.pointOfView({ lat: globedData[0].lat, lng: globedData[0].lon, altitude: 4 })
    world.labelsData(globedData)
    world.objectsData(globedData)
    world.controls().autoRotate = true;
    world.controls().autoRotateSpeed = 0.1;
  }
});


const loadingTexts = ["Bäume pflanzen...", "Grünflächen pflegen...", "Gebäude planen...", "Straßen markieren...", "Ampeln aufstellen...", "Wasserbecken füllen...", "Orte markieren...", "", "...gleich geschafft...", "", "...die Internetverbindung scheint langsam...", "... haben Sie noch einen Moment Geduld, falls die Seite nicht lädt, probieren sie bitte einen anderen Browser!"]
const curLoadingText = ref("Karte wird befüllt...")

const showLoadingText = ref(true)
async function animate() {
  let i = 0
  const interval = setInterval(function () {
    curLoadingText.value = loadingTexts[i]

    if (showLoadingText.value == false) {
      i++
      showLoadingText.value = true
    }
    else {
      showLoadingText.value = false
    }
    if (i >= loadingTexts.length) {
      clearInterval(interval)
      i = 0
    }
  }, 1000);
}


animate();
</script>

<style scoped>
#loading-screen-wrapper {
  width: 100%;
  height: 100vh;
  display: block;
  justify-content: center;
  align-items: center;
  background-color: #1C1C1E;


}

.UcodeLogo {

  animation: append-animate 0.5s ease-out;
}

.logo-container {
  position: absolute;
  top: 10px;
  width: 100%;
  text-align: center;
  min-height: 50px;
  color: black;
}

.LoadingText {
  position: absolute;
  bottom: 20px;
  width: 100%;
  text-align: center;
  min-height: 50px;
  color: black;
}


/* Animation */
/* Logo      */
@keyframes append-animate {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }

  75% {
    transform: scale(1.05);
    opacity: 0.75;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Text */
.fade-enter-active {
  transition: all .3s ease-in;
}

.fade-leave-active {
  transition: all .3s ease-in;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.main-container {
  position: absolute;
  z-index: 9999
}
</style>