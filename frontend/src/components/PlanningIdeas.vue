<template>
  <v-sheet class="mx-auto planning-ideas-options">
    <v-btn v-if="store.state.ui.planningIdeasLoaded" :key="100" height="32px" size="small"
      :variant="activeBtn == 100 ? 'tonal' : undefined" rounded="lg" flat
      @click="activateSelectedPlanningIdea(planningData.routes); setActiveBtn(100)">
      Alle
    </v-btn>
    <div v-for="route in planningData.routes.features" :key="route.properties.id">

      <v-btn height="32px" size="small" class="ml-2" rounded="lg" flat
        @click="activateSelectedPlanningIdea(route); setActiveBtn(route.properties.id); exploreSelectedPlanningIdea(route.properties.id)"
        :variant="activeBtn == route.properties.id ? 'tonal' : undefined">
        <v-icon :color="route.properties.color">
          mdi-checkbox-blank-circle
        </v-icon>
        route {{ route.properties.id }}
      </v-btn>
    </div>
  </v-sheet>
</template>

<script lang="ts" setup>
import { onMounted, reactive, watch, ref } from "vue";
import { useStore } from "vuex";
import bbox from "@turf/bbox";
import {
  getRoutesFromDB
} from "../service/backend.service";
import { ThreejsSceneOnly } from "@/utils/ThreejsSceneOnly";
import { addLineFromCoordsAr1 } from "@/utils/ThreejsGeometryCreation";
import type { Feature } from "@turf/helpers";
import { Popup } from "maplibre-gl";
import { HTTP } from "@/utils/http-common";




const store = useStore();

const emit = defineEmits(["activateSelectedPlanningIdea", "fitBoundsToBBOX", "addPopup", "flyToLocation", "flyToLocation"])

let planningData = reactive<{routes: Feature[]}>({ routes: [] })

let activeBtn = ref(100)
let threeJsScene: any
let planningIdeaPopup = new Popup({ closeButton: false, closeOnClick: false })
let exploredPlanningIdeaId = reactive<number[]>([])
const setActiveBtn = (selectedId: any) => {
  activeBtn.value = selectedId
}

const addRouteToMap = async () => {

  await sendRouteRequest()
  // await sendRouteRequestTHREE()
}
onMounted(() => {
  addRouteToMap()
})
const createEmptyThreeJsScene = async () => {
  const threeJsSceneLayer = await ThreejsSceneOnly(store.state.aoi.projectSpecification.bbox.xmin, store.state.aoi.projectSpecification.bbox.ymin, "threeJsScenePlanning")
  threeJsScene = threeJsSceneLayer.scene
  store.commit("map/addLayer", threeJsSceneLayer.layer)
}
const sendRouteRequestTHREE = async () => {
  if (threeJsScene == undefined) {
    createEmptyThreeJsScene()
  }
  const routeData = await getRoutesFromDB(store.state.aoi.projectSpecification.project_id)
  planningData.routes = routeData.data
  if (routeData.data.features == null) {
    return
  }
  //  console.log(routeData)
  addLineFromCoordsAr1({
    scene: threeJsScene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: routeData.data,
    color: "custom",
    height: 0.5,
    extrude: 2
  })

  store.commit("ui/planningIdeasLoaded", true)
}
const sendRouteRequest = async () => {

  const routeData = await getRoutesFromDB(store.state.aoi.projectSpecification.project_id)

  if (routeData.data.features == null) {
    return
  }
  let baseWidth = 0.1; 
  let baseZoom = 10;
  planningData.routes = routeData.data
  store.commit("planningIdeas/addPlanningIdeaFeatures", routeData.data)
  store.commit("map/addSource", {
    id: "routes",
    geojson: {
      "type": "geojson",
      "data": routeData.data
    }
  })
  store.commit("map/addLayer", {
    'id': "routes",
    'type': 'line',
    'source': "routes",
    'layout': {
      'line-join': 'round',
      'line-cap': 'round',
    },
    'paint': {
      // 'line-color': [
      //     "match",
      //         ["get", "id"],
      //         1,
      //         "#d3504e",
      //         2,
      //         "#81d144",
      //         "#4e76d3",
      // ],//
      'line-color': ['get', 'color'],
      //'line-width': 5,
      'line-width':{
            stops: [[14, 4], [17, 6],[24, 35]]
      },
      /*'line-offset': {
        property: "id",
        type: "categorical",
        stops: [[1,-5], [2, 0], [3, -5]]
      },*/
      'line-offset':
          ['interpolate', ['linear'], ['zoom'],
            14,
            ['case',
                ["==", ["get", "id"], 1],
                -4,
                ["==", ["get", "id"], 3],
                -4,
                0
            ],
            17,
            ['case',
                ["==", ["get", "id"], 1],
                -6,
                ["==", ["get", "id"], 3],
                -6,
                0
            ],
            24,
            ['case',
                ["==", ["get", "id"], 1],
                -35,
                ["==", ["get", "id"], 3],
                -35,
                0
            ]
          ]
    }
  })
  // store.commit("map/addLayer", {
  //   "id": "routes-symbols",
  //   "type": "symbol",
  //   "source": "routes",
  //   "layout": {
  //     "symbol-placement": "line",
  //     "text-font": ["Open Sans Regular Bold"],
  //     "text-field": '{route_name}',
  //     "text-size": 10
  //   }
  // })
  store.commit("ui/planningIdeasLoaded", true)

};

const activateSelectedPlanningIdea = (route: Feature) => {
  // let activeRoute: THREE.Object3D=threeJsScene.getObjectByName(route.properties?.route_name)
  // console.log(activeRoute)
  // activeRoute.material.color.setHex("#ffffff");
  emit("activateSelectedPlanningIdea", route)
}

const exploreSelectedPlanningIdea = (routeId: number) => {
  if (store.state.quests.current_order_id == 0 && exploredPlanningIdeaId.indexOf(routeId) == -1) {
    let data = store.state.quests.questList[0].content.detailedDescription["route" + routeId]
    let start = 0
    let dataLength = data.length
    planningIdeaPopup.setLngLat(data[0].location.coordinates)
    planningIdeaPopup.setHTML(`<div id="planning-idea-popup-content">
                  <div id="description">${data[start].description} </div>
                  <div class="mt-4">
                    <button style="color: green; outline: none !important; box-shadow: none;" id="next" class="btn btn-sm mt-2">Weiter</button>
                  </div>
                </div>`
    )
    emit("addPopup", planningIdeaPopup)
    emit("flyToLocation", {
      center: data[start].location.coordinates,
      zoom: 19,
      bearing: 130,
      pitch: 60,
      essential: true
    })

    document.getElementById("next")!.onclick = () => {
      start += 1
      if (start <= dataLength - 1) {
        planningIdeaPopup.setLngLat(data[start].location.coordinates)
        document.getElementById("description")!.innerHTML = data[start].description
        emit("flyToLocation", {
          center: data[start].location.coordinates,
          zoom: 19,
          bearing: 130,
          pitch: 60,
          essential: true
        })

        if (start == dataLength - 1) {
          document.getElementById("next")!.innerHTML = "Fertig"
          document.getElementById("next")!.onclick = () => {
            planningIdeaPopup.remove()
            exploredPlanningIdeaId.push(routeId)
            store.state.quests.questList[0].fulfillment++
            addQuestFulfillment()
          }
        }
      }
    }
  }
  else {
    planningIdeaPopup?.remove()
  }
}

const addQuestFulfillment = async () => {
  await HTTP.get("add-quest-fulfillment", {
    params: {
      questId: store.state.quests.questList[0].quest_id,
      userId: store.state.aoi.userId
    }
  })

}
watch(store.state.quests, function (state) {
  if (state.current_order_id != 0) {
    planningIdeaPopup?.remove()
  }
});
watch(store.state.ui, function (state) {
  if (state.aoiMapPopulated == true && state.projectsLoaded == true && state.planningIdeasLoaded == true && state.intro == false) {
    const planningIdeaBBOX = bbox(planningData.routes);
    emit("fitBoundsToBBOX", planningIdeaBBOX)
  }
});

</script>

<style scoped>
.planning-ideas-options {
  position: sticky;
  bottom: 56px;
  margin-top: 5px;
  padding: 0.5rem;
  z-index: 999;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  -moz-backdrop-filter: blur(5px);
  -ms-backdrop-filter: blur(5px);
  overflow-x: scroll;
  scrollbar-width: none !important;
}

.planning-ideas-options::-webkit-scrollbar {
  display: none !important;
}

.col {
  color: #df4947;
  color: #82e139;
  color: #225de6;
}
</style>