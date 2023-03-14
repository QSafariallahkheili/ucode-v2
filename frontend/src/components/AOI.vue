<template>
  <DevUI v-if="devMode" @getMapOrientation="emit('getMapOrientation')" @addDrawControl="addDrawControl" :drawnPolygon="props.drawnPolygon"/>
</template>

<script lang="ts" setup>
import DevUI from "@/components/DevUI.vue";
import { addGeoOnPointsToThreejsScene, addLineFromCoordsAr1, addPolygonsFromCoordsAr } from '@/utils/ThreejsGeometryCreation';
import { ThreejsSceneOnly } from "@/utils/ThreejsSceneOnly";
import { computed, onMounted } from "vue";
import { useStore } from "vuex";
import {

  getbuildingsFromDB,
  getDrivingLaneFromDB,
  getGreeneryFromDBTexture,
  getGreeneryJsonFromDB,
  getTrafficSignalFromDB,
  getTreeJsonFromDB,
  getTreesFromDB,
  getWaterFromDB,
  getTrafficSignalDataFromDB,
  getbuildingsDataFromDB,
  getTramLineDataFromDB,
  getAmenities,
  getAmenityDataFromDB,
  getSidewalkFromDB,
  getBikeFromDB,
  getBikeLaneDataFromDB,
  getPedestrianAreaFromDB,
  getZerbraCrossFromDB,
  getRailsDataFromDB

} from "../service/backend.service";
import type { IControl } from "maplibre-gl";
import type { FeatureCollection } from "@turf/helpers";
const store = useStore();
const devMode = computed(() => store.getters["ui/devMode"]);
let threeJsScene3d: any;
let threeJsSceneFlat: any;

const emit = defineEmits(["addLayer", "addImage", "triggerRepaint", "getMapOrientation", "addDrawControl"]);
const props=defineProps(['drawnPolygon'])

const populateMap = async () => {
  // await sendBuildingRequest();
  await createEmptyThreeJsScene();
  await sendBikeLaneIconRequest()
  await sendBuildingRequestTHREE()
  // await sendGreeneryRequest();
  await addAmenities();
  await sendGreeneryRequestTHREE();
  // await sendTrafficSignalRequest();
  await sendTrafficSignalRequestTHREE();
  //  await sendDrivingLaneRequest();
  await sendDrivingLaneRequestTHREE();
  await sendTreeRequest();
  await sendWaterRequestTHREE();
  await createAoiPlane();
  // await sendTramLineRequest();
  await sendTramLineRequestTHREE();
  emit("addLayer", threeJsScene3d.layer)
  emit("addLayer", threeJsSceneFlat.layer, "routes")
  await sendSidewalkRequest();
  await sendBikeRequest()
  await sendPedestrianAreaRequest()
  await sendZerbraCrossRequest ()
  await sendRailsRequest ()
  
 
  store.dispatch("aoi/setMapIsPopulated");
  store.commit("ui/aoiMapPopulated", true);
}

onMounted(() => {
  populateMap();
})
const createEmptyThreeJsScene = async () => {
  threeJsScene3d = await ThreejsSceneOnly(store.state.aoi.projectSpecification.bbox.xmin, store.state.aoi.projectSpecification.bbox.ymin, "threeJsScene3d")
  threeJsSceneFlat = await ThreejsSceneOnly(store.state.aoi.projectSpecification.bbox.xmin, store.state.aoi.projectSpecification.bbox.ymin, "threeJsSceneFlat")
}

const sendBuildingRequestTHREE = async () => {
  const buildingData = await getbuildingsDataFromDB(store.state.aoi.projectSpecification.project_id);
  if(!buildingData.features){
    console.log('No Data in bd for buildings!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsScene3d.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: buildingData,
    color: ['#C8D6E8', '#A5B1C2', '#BAC3C9'],
    height: 0,
    extrude: .99
  })
};
const sendBuildingRequest = async () => {
  const newLayer = await getbuildingsFromDB(store.state.aoi.projectSpecification.project_id);
  emit("addLayer", newLayer);

};
const addAmenities =  async () => {
  const amenityData = await getAmenityDataFromDB(store.state.aoi.projectSpecification.project_id);
  if(amenityData.features.length == 0){
    console.log('No Data in bd for amenities!')
    return
  }
  const amenitiesAr: string[] = []
  const groupedAmenities: {"type": string , "featureCollection":FeatureCollection}[]= []
  amenityData.features.forEach((feat)=>{
    // console.log(amenitiesAr.includes(feat.properties?.amenity))
    if(!amenitiesAr.includes(feat.properties?.amenity)){
      amenitiesAr.push(feat.properties?.amenity)
      groupedAmenities.push({type : feat.properties?.amenity, featureCollection: {type: "FeatureCollection", features:[]}})
    }
    groupedAmenities.forEach((amenity)=>{
      if(amenity.type == feat.properties?.amenity){
        amenity.featureCollection.features.push(feat)
      }
    })
  })
  // console.log(groupedAmenities)
  groupedAmenities.forEach((anemity) =>{
    addGeoOnPointsToThreejsScene(threeJsScene3d.scene,anemity.featureCollection,"poiIcons/"+anemity.type+".glb",store.state.aoi.projectSpecification.bbox,[40,40],true)
  })
};
const sendGreeneryRequest = async () => {
  const newLayer = await getGreeneryFromDBTexture(store.state.aoi.projectSpecification.project_id);
  emit("addLayer", newLayer);

};
const sendGreeneryRequestTHREE = async () => {
  const greeneryJson: FeatureCollection = await getGreeneryJsonFromDB(store.state.aoi.projectSpecification.project_id);
  // console.log(greeneryJson)
  if(!greeneryJson.features){
    console.log('No Data in bd for greenery!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: greeneryJson,
    color: "#9EBB64",
    height: 0,
    extrude: 0.15
  })


};
const sendWaterRequestTHREE = async () => {
  const waterJson: FeatureCollection = await getWaterFromDB(store.state.aoi.projectSpecification.project_id);
  // console.log(waterJson)
  if(!waterJson.features){
    console.log('No Data in bd for water!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: waterJson,
    color: "#64A4BB",
    height: 0,
    extrude: 0.2
  })


};
const createAoiPlane = async () => {
  // console.log("AOIPlane")
  const data: FeatureCollection = {
    'type': 'FeatureCollection',//redo as polygon..be smart
    'features': [
      {
        'type': 'Feature',
        'geometry': {
          'type': 'Polygon',
          'coordinates':
            [[[store.state.aoi.projectSpecification.bbox.xmin, store.state.aoi.projectSpecification.bbox.ymin],
            [store.state.aoi.projectSpecification.bbox.xmax, store.state.aoi.projectSpecification.bbox.ymin],
            [store.state.aoi.projectSpecification.bbox.xmax, store.state.aoi.projectSpecification.bbox.ymax],
            [store.state.aoi.projectSpecification.bbox.xmin, store.state.aoi.projectSpecification.bbox.ymax]]]
        },
        'properties': {}
      }
    ]
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: data,
    color: "#E8E8E8",
    height: 0,
    extrude: 0
  })
}
const sendTreeRequest = async () => {

  const treeJson: FeatureCollection = await getTreeJsonFromDB(store.state.aoi.projectSpecification.project_id);
  if(!treeJson.features){
    console.log('No Data in bd for trees!')
    return
  }
  let trees: string[] = ["Tree_01.glb", "Tree_02.glb", "Tree_03.glb"]
  let ArrayIndex: number[] = []
  treeJson.features.forEach(() => {
    let int = Math.round((Math.random() * ((trees.length - 1) - 0)) + 0)
    ArrayIndex.push(int)
  })
  trees.forEach((tree, _index) => {
    let partJson: { type: string, features: any[] } = { type: "FeatureCollection", features: [] }
    treeJson.features.forEach((feature, index) => {
      if (ArrayIndex[index] == _index) {
        partJson.features.push(feature)
      }
    })
    addGeoOnPointsToThreejsScene(threeJsScene3d.scene, partJson, "TreeVariants/" + tree, store.state.aoi.projectSpecification.bbox, [0.7, 0.8], true)

  })

}


const sendDrivingLaneRequestTHREE = async () => {
  const drivingLanedata: { lane: FeatureCollection, polygon: FeatureCollection } = await getDrivingLaneFromDB(store.state.aoi.projectSpecification.project_id)
  if(!drivingLanedata.polygon.features){
    console.log('No Data in bd for driving lanes!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: drivingLanedata.polygon,
    color: "#262829",
    height: 0,
    extrude: 0.3
  })
  store.commit("map/addSource", {
    id: "driving_lane",
    geojson: {
      "type": "geojson",
      "data": drivingLanedata.lane
    }
  })
  let baseWidth = 0.2;
  let baseZoom = 15;
  store.commit("map/addLayer", {
    'id': "driving_lane",
    'type': 'line',
    'source': "driving_lane",
    'layout': {
      'line-join': 'round',
      'line-cap': 'round'
    },
    'paint': {
      'line-color': '#FFFFFF',
      //'line-width': 1,
      "line-width": 
            {
                'type': 'exponential',
                'base': 2,
                'stops': [
                    [0, baseWidth * Math.pow(2, (0 - baseZoom))],
                    [22, baseWidth * Math.pow(2, (22 - baseZoom))]
                ]
            },
      'line-dasharray': [4,20]
    }
  })


}
const sendDrivingLaneRequest = async () => {
  const drivingLanedata = await getDrivingLaneFromDB(store.state.aoi.projectSpecification.project_id)

  store.commit("map/addSource", {
    id: "driving_lane_polygon",
    geojson: {
      "type": "geojson",
      "data": drivingLanedata.polygon
    }
  })
  store.commit("map/addLayer", {
    'id': "driving_lane_polygon",
    'type': 'fill',
    'source': "driving_lane_polygon",
    'paint': {
      'fill-color': '#798999',
      'fill-opacity': 1
    }
  })

  store.commit("map/addSource", {
    id: "driving_lane",
    geojson: {
      "type": "geojson",
      "data": drivingLanedata.lane
    }
  })
  store.commit("map/addLayer", {
    'id': "driving_lane",
    'type': 'line',
    'source': "driving_lane",
    'layout': {
      'line-join': 'round',
      'line-cap': 'round'
    },
    'paint': {
      'line-color': '#FFFFFF',
      'line-width': 1,
      'line-dasharray': [10, 20]
    }
  })

}


const sendTrafficSignalRequest = async () => {

  const trafficSignalLayer = await getTrafficSignalFromDB(store.state.aoi.projectSpecification.project_id);
  emit("addLayer", trafficSignalLayer)

}

const sendTramLineRequestTHREE = async () => {
  const tramLaneData = await getTramLineDataFromDB(store.state.aoi.projectSpecification.project_id);
  if(!tramLaneData.features){
    console.log('No Data in bd for tram lines!')
    return
  }
  addLineFromCoordsAr1({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: tramLaneData,
    color: "#676767",
    height: 0.2,
    extrude: .12
  })

}
const sendTramLineRequest = async () => {


  const tramLaneData = await getTramLineDataFromDB(store.state.aoi.projectSpecification.project_id);
  store.commit("map/addSource", {
    id: "tram_line",
    geojson: {
      type: "geojson",
      data: tramLaneData.data,
    },
  });
  store.commit("map/addLayer", {
    id: "tram_line",
    type: "line",
    source: "tram_line",
    layout: {
      "line-join": "round",
      "line-cap": "round",
    },
    paint: {
      "line-color": "#FFFF00",
      "line-width": 2

    },
  });

}

const sendTrafficSignalRequestTHREE = async () => {

  const trafficSignalData = await getTrafficSignalDataFromDB(store.state.aoi.projectSpecification.project_id);
  if(!trafficSignalData.features){
    console.log('No Data in bd for traffic signals!')
    return
  }
  addGeoOnPointsToThreejsScene(threeJsScene3d.scene, trafficSignalData, "TrafficLight.glb", store.state.aoi.projectSpecification.bbox)
}

const sendSidewalkRequest = async () =>{
  
  const sidewalkData = await getSidewalkFromDB(store.state.aoi.projectSpecification.project_id)
  if(!sidewalkData.features){
    console.log('No Data in bd for side walks!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: sidewalkData,
    color: "#bdb8aa",
    height: 0,
    extrude: 0.25
  })
}

const sendBikeRequest = async () =>{
  
  const bikeLaneData = await getBikeFromDB(store.state.aoi.projectSpecification.project_id)
  if(!bikeLaneData.features){
    console.log('No Data in bd for bike lanes!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: bikeLaneData,
    color: "#f75d52",
    height: 0,
    extrude: 0.28
  })  
   
}

const sendBikeLaneIconRequest = async () => {

  const bikeLaneData = await getBikeLaneDataFromDB(store.state.aoi.projectSpecification.project_id);
  if(!bikeLaneData.features){
    console.log('No Data in bd for bike lanes!')
    return
  }
  let baseWidth = 0.0011
  let baseZoomm = 15
  store.commit("map/addSource", {
    id: "bike-icon",
    geojson: {
      type: "geojson",
      data: bikeLaneData,
    },
  });
  store.commit("map/addLayer", {
    id: "bike-icon",
    type: "symbol",
    source: "bike-icon",
    
    layout: {
      'symbol-placement': "line",
      'symbol-spacing': 1,
      'icon-allow-overlap': true,     
      'icon-ignore-placement': false,
      'icon-image': 'bike.png',
      'icon-size': {
              'type': 'exponential',
              'base': 2,
              'stops': [
                  [0, baseWidth * Math.pow(2, (0 - baseZoomm))],
                  [22, baseWidth * Math.pow(2, (22 - baseZoomm))]
              ]
          },
      'visibility': 'visible',
      'icon-rotate': 90,
    },
    paint: {
      'icon-opacity': 0.7,
      'icon-color': '#ffffff'
    }
  });
}

const sendPedestrianAreaRequest = async () => {
  const pedestrianAreaData = await getPedestrianAreaFromDB(store.state.aoi.projectSpecification.project_id)
  if(!pedestrianAreaData.features){
    console.log('No Data in bd for pedestrian areas!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: pedestrianAreaData,
    color: "",
    height: 0,
    extrude: 0.2,
    textureURL: "pattern-pedestrian.jpeg"
  }) 
}

const sendZerbraCrossRequest = async () => {
  const zerbraCrossingData = await getZerbraCrossFromDB(store.state.aoi.projectSpecification.project_id)
  if(!zerbraCrossingData.features){
    console.log('No Data in bd for zebra crossings!')
    return
  }
  addPolygonsFromCoordsAr({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: zerbraCrossingData,
    color: "#ffffff",
    height: 0,
    extrude: 0.32
  })  
}

const sendRailsRequest = async () => {
  const railsData = await getRailsDataFromDB(store.state.aoi.projectSpecification.project_id);
  if(!railsData.features){
    console.log('No Data in bd for tram lines!')
    return
  }
  addLineFromCoordsAr1({
    scene: threeJsSceneFlat.scene,
    bbox: store.state.aoi.projectSpecification.bbox,
    geoJson: railsData,
    color: "#676767",
    height: 0.2,
    extrude: .12
  })

}

const addDrawControl = (control: IControl) =>{
  emit('addDrawControl', control)

}
</script>

<style scoped>

</style>