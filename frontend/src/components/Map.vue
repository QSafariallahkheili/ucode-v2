<template>
    <div class="map-wrap" ref="mapContainer">
      <div class="map" id="map">
        <AOI v-if="mapStyleLoaded" @addLayer="addLayerToMap" @addImage="addImageToMap" @triggerRepaint="triggerRepaint" />
        <ProjectInfo :show="tabIndex=='projectInfo'" />
        <Suspense>
          <Quests v-show="tabIndex=='planning'" :hide="hideQuests" @hideQuests="() => {hideQuests = !hideQuests}"/>
        </Suspense>
        
        <PlanningIdeas v-show="store.state.ui.intro==false && tabIndex=='planning'" v-if="mapStyleLoaded" @activateSelectedPlanningIdea="activateSelectedPlanningIdeaInMap"
            @navigateToPlanningIdea="navigateToPlanningIdea" @addPopup="addPopupToMap" @flyToLocation="flyToLocation" />
        <FreeComment v-show="tabIndex=='planning'" @placeComment="placeComment" :showCommentDialog="showCommentDialog" @addComment="addCommentToMap"
          @closeCommentDialog="closeCommentDialog" @hideQuests="() => {hideQuests = true}"/>
        <CommentGallery 
          :show="tabIndex=='discussion'" 
          @deleteQuestCommentFromSource="deleteQuestCommentFromSource" 
          @scaleUpComment="scaleUpComment"
          @toggleCommentLayerVisibility="togglelayerVisibility"
          @updateCommentSource="addSourceToMap"
          @addImage="addImageToMap"
        />
        
        <BottomNavigation v-show="store.state.ui.intro==false" @tabIndexChanged="switchView" :tabIndex="tabIndex"/>
        <Contribution @addPopup="addPopupToMap" @addDrawControl="addDrawControl" @addDrawnLine="addDrawnLine"
          @removeDrawnLine="removeDrawnLine" @removeDrawControl="removeDrawControl"
          :clickedCoordinates="mapClicks.clickedCoordinates" :lineDrawCreated="lineDrawCreated" />
        <Comment @removePulseLayer="removePulseLayerFromMap" />
        <Intro  v-show="store.state.ui.intro"/>
      </div>

  </div>
</template>


<script lang="ts" setup>
import AOI from "@/components/AOI.vue";
import Comment from "@/components/Comment.vue";
import Contribution from "@/components/Contribution.vue";
import PlanningIdeas from "@/components/PlanningIdeas.vue";
import Quests from "@/components/Quests.vue";
import FreeComment from "@/components/FreeComment.vue";
import BottomNavigation from "@/components/BottomNavigation.vue";
import CommentGallery from "@/components/CommentGallery.vue";
import Intro from "@/components/Intro.vue";
import ProjectInfo from "@/components/ProjectInfo.vue"
import type { ProjectSpecification } from "@/store/modules/aoi";
import { HTTP } from "@/utils/http-common";
import { pulseLayer } from "@/utils/pulseLayer";
import { MapboxLayer } from "@deck.gl/mapbox/typed";
import { ScenegraphLayer } from "@deck.gl/mesh-layers/typed";
import * as turf from '@turf/turf';
import { Map, type CustomLayerInterface, type Feature, type IControl, type LayerSpecification, type LngLatBoundsLike, type LngLatLike, Popup, Marker } from "maplibre-gl";
import { computed, onMounted, onUnmounted, reactive, ref, shallowRef, watch } from "vue";
import { useStore } from "vuex";
import { deckLightingEffect } from "@/utils/deckLighting";


const store = useStore();

const devMode = computed(() => store.getters["ui/devMode"]);

const mapContainer = shallowRef(null);
let map: Map = {} as Map;
const mapClicks = reactive({ clickedCoordinates: [] })
const commentClicks = reactive<{ commentCoordinates: number[] }>({ commentCoordinates: [] })
let lineDrawCreated = ref(0)
let mapStyleLoaded = ref(false)
let tabIndex = ref("planning")
let showCommentDialog = ref(false)
let hideQuests = ref(false)
//let activeMarker = reactive<any>({});



let unsubscribeFromStore = () => { };

onUnmounted(() => {
  unsubscribeFromStore()
})

onMounted(() => {
  let vh = window.innerHeight * 0.01;
  // Then we set the value in the --vh custom property to the root of the document
  document.documentElement.style.setProperty('--vh', `${vh}px`);

  // We listen to the resize event
  window.addEventListener('resize', () => {
    // We execute the same script as before
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  });
  map = new Map({
    container: mapContainer.value ?? "",
    style: store.state.map.style,
    center: [store.state.map.center.lng, store.state.map.center.lat],
    zoom: store.state.map.zoom,
    minZoom: store.state.map.minZoom,
    maxZoom: store.state.map.maxZoom,
    maxPitch: store.state.map.maxPitch,
    attributionControl: false,
    antialias: true
  });


  map.on("load", function () {
    mapStyleLoaded.value = true
    addImageToMap("bike.png")
    unsubscribeFromStore = store.subscribe((mutation, state) => {
      if (mutation.type === "map/addLayer") {
        state.map.layers?.slice(-1).map(addLayerToMap)
      }
      if (mutation.type === "map/addSource") {
        state.map.sources?.slice(-1).map(addSourceToMap)
      }
    });

    const projectSpecification: ProjectSpecification = store.state.aoi.projectSpecification;

    map.fitBounds([projectSpecification.bbox.xmin,
    projectSpecification.bbox.ymin,
    projectSpecification.bbox.xmax,
    projectSpecification.bbox.ymax]);

    HTTP.get("").then((response) => {
      // console.log(response);
    })

    //  getCommentData()

  });
  map.on('click', function (mapClick) {
    // @ts-ignore
    mapClicks.clickedCoordinates = [mapClick.lngLat.lng, mapClick.lngLat.lat]
    if (store.state.comment.toggle) {
      //@ts-ignore
      addLayerToMap(pulseLayer(store.state.pulse.pulseCoordinates.geometry.coordinates))
    }

  });

  map.on('click', 'allComments', function (e) {    
    // @ts-ignore
    document.getElementById(e.features[0].properties.id).scrollIntoView({behavior: 'smooth'}, true);
    // @ts-ignore
    map.setLayoutProperty('allComments', 'icon-size', ['match', ['get', 'id'], e.features[0].properties.id, 0.4 , 0.15]);

  });

  map.on('draw.create', () => {
    lineDrawCreated.value = 1
  })

  map.on('draw.create', () => {
    lineDrawCreated.value = 1
  })

});

const triggerRepaint = () => {
  map.triggerRepaint()
}
// threejs layer
const addThreejsShape = () => {
  // @ts-ignore
  addLayerToMap(TreeModel(13.74647, 51.068646, 100));
  map.triggerRepaint()
}
const placeComment = () => {
  showCommentDialog.value = true
  store.state.freecomment.moveableCommentMarker
    .setLngLat([map.getCenter().lng, map.getCenter().lat])
    .addTo(map);
}
const addCommentToMap = (source: any, layer: any) => {
  addSourceToMap(source)
  if (!map.hasImage('comment.png')) {
    map?.loadImage('comment.png', (error, image) => {
      if (error) throw error;
      map?.addImage('comment.png', image!);
       addLayerToMap(layer)
    });
  }
  else {
    addLayerToMap(layer)
  }
}

const addLayerToMap = (layer: LayerSpecification | CustomLayerInterface, beforeLayer?: string) => {
  // console.log(layer.id)
  const addedlayer = map.getLayer(layer.id)
  if (typeof addedlayer !== 'undefined') {
    removeLayerFromMap(layer.id)
  }

  if (!layer) return;
  // @ts-ignore
  if (layer.paint) {
    // @ts-ignore
    if (layer.paint["fill-pattern"]) {
      // @ts-ignore
      addImageToMap(layer.paint["fill-pattern"]);
    }
  }
  if (beforeLayer && map.getLayer(beforeLayer) == undefined) {
    beforeLayer = ""
  }
  map?.addLayer(layer, beforeLayer ? beforeLayer : "");
  const layerHirarchy: any[] = []// = reactive<[{layer: any, orderId: Number}]>([{}])

  const buildinglayer = map.getLayer("overpass_buildings")
  // @ts-ignore
  buildinglayer?.implementation?.deck.setProps({
    effects: [deckLightingEffect]
  });

  if (typeof buildinglayer !== 'undefined') {
    layerHirarchy.push({ layer: buildinglayer, orderId: 99 })
  }
  const greenerylayer = map.getLayer("overpass_greenery")
  if (typeof greenerylayer !== 'undefined') {
    layerHirarchy.push({ layer: greenerylayer, orderId: 10 })
  }
  const commentlayer = map.getLayer("comments")
  if (typeof commentlayer !== 'undefined') {
    layerHirarchy.push({ layer: commentlayer, orderId: 90 })
  }
  const drivinglanelayer = map.getLayer("driving_lane_polygon")
  if (typeof drivinglanelayer !== 'undefined') {
    layerHirarchy.push({ layer: drivinglanelayer, orderId: 60 })
  }
  const drivinglane = map.getLayer("driving_lane")
  if (typeof drivinglane !== 'undefined') {
    layerHirarchy.push({ layer: drivinglane, orderId: 70 })
  }
  const treeLayer = map.getLayer("trees")
  if (typeof treeLayer !== 'undefined') {
    layerHirarchy.push({ layer: treeLayer, orderId: 80 })
  }
  const treeLayer3js = map.getLayer("TreeVariants/Tree_02.glb")
  if (typeof treeLayer3js !== 'undefined') {
    layerHirarchy.push({ layer: treeLayer3js, orderId: 80 })
  }
  const routesLayer = map.getLayer("routes")
  if (typeof routesLayer !== 'undefined') {
    layerHirarchy.push({ layer: routesLayer, orderId: 1 })
  }
  const routesSymbolLayer = map.getLayer("routes-symbols")
  if (typeof routesSymbolLayer !== 'undefined') {
    layerHirarchy.push({ layer: routesSymbolLayer, orderId: 76 })
  }
  const ownCommentLayer = map.getLayer("ownComments")
  if (typeof ownCommentLayer !== 'undefined') {
    layerHirarchy.push({ layer: ownCommentLayer, orderId: 100 })
  }
  const ThreeJsScene3d = map.getLayer("threeJsScene3d")
  if (typeof ThreeJsScene3d !== 'undefined') {
    layerHirarchy.push({ layer: ThreeJsScene3d, orderId: 2 })
  }
  const ThreeJsSceneFlat = map.getLayer("threeJsSceneFlat")
  if (typeof ThreeJsSceneFlat !== 'undefined') {
    layerHirarchy.push({ layer: ThreeJsSceneFlat, orderId: 0 })
  }

  // const TramLayer = map.getLayer("tram_line")
  // if (typeof TramLayer !== 'undefined') {
  //   layerHirarchy.push({ layer: TramLayer, orderId: 90 })
  // }




  // for (let index = 0; index < layerHirarchy.length; index++) {
  //   const x = layerHirarchy[index];
  //     for (let index = 0; index < layerHirarchy.length; index++) {
  //       const y = layerHirarchy[index];
  //        if(x.layer !== y.layer && x.orderId>y.orderId){
  //          map.moveLayer(y.layer.id,x.layer.id)
  //          console.log("move layer " + x.layer.id + " over " +y.layer.id)
  //         //  console.log("map.moveLayer("+y.layer.id+","+x.layer.id+")")
  //        }
  //   }
  // }

  // if (typeof buildinglayer !== 'undefined' && typeof greenerylayer !== 'undefined') {
  //   map?.moveLayer("overpass_greenery", "overpass_buildings")
  // }
  // if (typeof commentlayer !== 'undefined' && typeof greenerylayer !== 'undefined') {
  //   map?.moveLayer("overpass_greenery", "comments")
  // }
  // if (typeof drivinglanelayer !== 'undefined' && typeof commentlayer !== 'undefined') {
  //   map?.moveLayer("driving_lane_polygon", "comments")
  // }
  // if (typeof drivinglane !== 'undefined' && typeof commentlayer !== 'undefined') {
  //   map?.moveLayer("driving_lane", "comments")
  // }
  // if (typeof drivinglanelayer !== 'undefined' && typeof buildinglayer !== 'undefined') {
  //   map?.moveLayer("overpass_buildings", "driving_lane_polygon")
  // }
  // if (typeof drivinglane !== 'undefined' && typeof buildinglayer !== 'undefined') {
  //   map?.moveLayer("overpass_buildings", "driving_lane")
  // }
  // if (typeof greenerylayer !== 'undefined' && typeof treeLayer !== 'undefined') {
  //   map?.moveLayer("overpass_greenery", "trees")
  // }
  // if (typeof drivinglanelayer !== 'undefined' && typeof treeLayer !== 'undefined') {
  //   map?.moveLayer("driving_lane_polygon", "trees")
  // }
  // if (typeof drivinglane !== 'undefined' && typeof treeLayer !== 'undefined') {
  //   map?.moveLayer("driving_lane", "trees")
  // }
  // if (typeof routesLayer !== 'undefined' && typeof treeLayer !== 'undefined') {
  //   map?.moveLayer("routes", "trees")
  // }
  // if (typeof routesSymbolLayer !== 'undefined' && typeof treeLayer !== 'undefined') {
  //   map?.moveLayer("routes-symbols", "trees")
  // }
  // if(typeof ownCommentLayer !== 'undefined'){
  //   map.moveLayer('ownComments')
  // }


};

const removeLayerFromMap = (layerId: string) => {
  if (map.getLayer(layerId)) {
    map.removeLayer(layerId);
  }
}

const addSourceToMap = (source: { id: string, geojson: any }) => {
  // console.log(source)
  if (!source) return;
  if (!map) return;
  //TODO extract this as a function parameter
  let sourceId = source.id;
  /*if (map.getSource(sourceId)) {
    map.removeSource(sourceId)
    removeLayerFromMap(sourceId)
  }*/

  if (map.getSource(sourceId) !== undefined) {
    let data = source.geojson.data
    //@ts-ignore
    map.getSource(sourceId).setData(data)
  }
  else {
    map.addSource(sourceId, source.geojson);
  }

};

const addImageToMap = (imgUrl: string) => {
  if (!imgUrl) return;
  if (!map.hasImage(imgUrl)) {
    map?.loadImage(imgUrl, (error, image) => {
      if (error) throw error;
      map?.addImage(imgUrl, image!);
    });
  }
};
const scaleUpComment = (hoveredCommentId: number) =>{
  map.setLayoutProperty('allComments', 'icon-size', ['match', ['get', 'id'], hoveredCommentId, 0.4 , 0.15]);
}

const togglelayerVisibility = (layerId:any, visbilityStatus: string) =>{
  const layer = map.getLayer(layerId)
  if (typeof layer !== 'undefined') {
    map.setLayoutProperty(layerId, 'visibility', visbilityStatus);
  }
}

// deckgl layder
const addDeckglShape = () => {
  const myDeckLayer = new MapboxLayer({
    id: "hexagon2D",
    // @ts-ignore
    type: ScenegraphLayer,
    data: [13.755453, 51.067814],
    pickable: true,
    scenegraph:
      "./GenericNewTree.glb",
    getPosition: [13.755453, 51.067814],
    getOrientation: () => [0, 0, 90],
    sizeScale: 50,
    _lighting: "pbr",
  }) as unknown as CustomLayerInterface;
  addLayerToMap(myDeckLayer);
};

const addPopupToMap = (popup: Popup) => {
  popup?.addTo(map)
}

const addDrawControl = (draw: IControl) => {
  map?.addControl(draw, 'bottom-right');
}

const addDrawnLine = (drawnPathlayer: CustomLayerInterface, linePopup: Popup) => {
  addLayerToMap(drawnPathlayer)
  linePopup?.addTo(map)
}

const removeDrawnLine = (draw: unknown, drawnPathlayerId: string) => {
  removeLayerFromMap(drawnPathlayerId)
}

const removeDrawControl = (draw: IControl, drawnPathlayerId: string) => {
  lineDrawCreated.value = 0
  map.removeControl(draw)
}

const removePulseLayerFromMap = (layerid: string) => {
  removeLayerFromMap(layerid)
  cancelAnimationFrame(store.state.pulse.pulseAnimationActivation)
}



const activateSelectedPlanningIdeaInMap = (selectedFeature: Feature) => {
  store.state.quests.selectedRouteId = null
  const currentBearing = map.getBearing();
  let bounds = turf.bbox(selectedFeature) as LngLatBoundsLike;
  map.fitBounds(bounds, { pitch: 40, bearing: currentBearing, padding: 40 });

  // @ts-ignore
  if (selectedFeature.type == 'FeatureCollection') {


    map.setPaintProperty('routes', 'line-color', ['get', 'color']);
  } else {
    store.state.quests.selectedRouteId = selectedFeature.properties.id
    map.setPaintProperty(
      'routes',
      'line-color',
      ['match', ['get', 'id'], selectedFeature.properties.id, selectedFeature.properties.color, 'rgba(0,0,0,0.4)' /*['get', 'color']*/],
    )
  }
}


const navigateToPlanningIdea = (planningIdeaBBOX: LngLatBoundsLike) => {

  setTimeout(() => {
    map.fitBounds(planningIdeaBBOX, {
      pitch: 60,
      duration: 3000,
      curve: 4,
    });
  }, 1000);
}

const flyToLocation = (flyOptions:any)=>{
  map.flyTo(flyOptions)
}

const switchView = (newTabIndex: string) => {
  tabIndex.value = newTabIndex
}

const closeCommentDialog = () => {
  showCommentDialog.value = false;
  hideQuests.value = false;
}

const deleteQuestCommentFromSource = (deletedComment: Feature[])=>{
  const ownCommentLayer = map.getLayer("ownComments")
  if (typeof ownCommentLayer !== 'undefined') {
    //@ts-ignore
    let comments = map.getSource("ownComments")?._data
    for (let i=0; i<comments.features.length; i++){
      for (let j=0; j<deletedComment?.length; j++){
        //@ts-ignore
        if (Number(comments.features[i]?.geometry?.coordinates[0])?.toFixed(5)==Number(deletedComment[j]?.geometry?.coordinates[0])?.toFixed(5) && Number(comments.features[i]?.geometry?.coordinates[1])?.toFixed(5)==Number(deletedComment[j]?.geometry?.coordinates[1])?.toFixed(5)){
            comments.features.splice(i, 1);
            //@ts-ignore
            map.getSource("ownComments")?.setData(comments);
        }
      }
    }
  }
}


onUnmounted(() => {
  map?.remove();
});
</script>

<style scoped>
.map-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  /* height: calc(var(--vh, 1vh) * 100); */
}

.map {
  height: 100%;
  width: 100%;
  position: absolute;
  /* background-color: darkgray; */
  background: linear-gradient(rgba(195, 245, 255, 1), rgba(255, 199, 111, 1));
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}
</style>