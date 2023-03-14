<template>
  <div v-show="showUITemp" v-if="showProjectInit" class="card-container">
    <div class="card">
      <v-btn variant="plain" icon class="close-button" @click="closeWindow">
        <v-icon>mdi-close</v-icon>
      </v-btn>
      <div class="card-content">
        <h2 class="mb-4 text-center">Initialize new project</h2>
        <div class="form-group">
          <label for="project-id">Project ID</label>
          <input type="text" id="project-id" v-model="projectSetupInfo.project_id" class="form-control" />
        </div>
        <div class="form-group">
          <label for="project-name">Project Name</label>
          <input type="text" id="project-name" v-model="projectSetupInfo.project_name" class="form-control" />
        </div>
        <div class="bounding-box-container">
          <div class="bounding-box-input">
            <label for="bbox">Bounding Box (bbox)</label>
            <input type="text" id="bbox" v-model="projectSetupBboxString" class="form-control" />
          </div>
          <div v-if="projectSetupBboxString == undefined || projectSetupBboxString.length == 0"
            class="bounding-box-button">
            <button class="btn" @click="getBbox">
              get
            </button>
          </div>
        </div>
        <div class="form-group">
          <label for="project-type">Project Type</label>
          <input type="text" id="project-type" v-model="projectSetupInfo.project_type" class="form-control" />
        </div>
        <div class="form-group">
          <label for="project-goal">Project Goal</label>
          <input type="text" id="project-goal" v-model="projectSetupInfo.project_goal" class="form-control" />
        </div>
        <div class="form-group">
          <label for="project-json">ProjectSetupInformation JSON *no other field is required*</label>
          <input type="text" id="project-json" v-model="newProjectJson" class="form-control" />
        </div>
        <div class="form-group">
          <label for="project-json">password *always required*</label>
          <input type="text" id="project-json" v-model="apiKey" class="form-control" />
        </div>
        <div class="button-container">
          <button class="btn btn-primary mt-4" @click="setupNewProject()">
            Setup New Project now!
          </button>
        </div>
      </div>
    </div>
  </div>
  <v-col v-show="showUITemp" cols="6" md="3" style="position:absolute; left: 0; top:50px; z-index:999; width:800px">
    <v-btn color="#41b883" class="mt-2" @click="clearServerCache">
      Clear server cache
    </v-btn>

    <!-- <v-btn color="success" class="ml-1" @click="getFilteredCommentData">
      Show filtered comments
    </v-btn> -->
    <v-btn color="#41b883" class="mt-2" @click="dropCommentData">
      Delete project comments
    </v-btn>
    <v-btn color="#41b883" class="mt-2" @click="ShoQuestsFulfillment">
      Show quest data
    </v-btn>
    <v-btn color="#41b883" @click="loadAllPoiFeaturesFromOSMall()" class="mt-2">
      Import all features from OSM
    </v-btn>
    <v-btn color="#41b883" @click="emit('getMapOrientation')" class="mt-2">
      Update Starting Orientation
    </v-btn>
    <v-btn color="#41b883" @click="showProjectInit = !showProjectInit" class="mt-2">
      Create New Project
    </v-btn>

  </v-col>

  <v-col v-show="showUITemp" cols="6" md="3" style="position: absolute; right: 0; top: 50px; z-index: 999">

    <v-select :items="['get from OSM']" label="building" variant="outlined" @update:modelValue="sendBuildingRequest">
    </v-select>
    <v-select :items="['get from OSM']" :label="$t('AOI.greenery')" variant="outlined"
      @update:modelValue="sendGreeneryRequest"></v-select>
    <v-select :items="['get from OSM']" label="tree" variant="outlined" @update:modelValue="sendTreeRequest">
    </v-select>
    <v-select :items="['get from OSM']" label="driving lane" variant="outlined"
      @update:modelValue="sendDrivingLaneRequest"></v-select>
    <v-select :items="['get from OSM']" label="traffic signal" variant="outlined"
      @update:modelValue="sendTrafficSignalRequest"></v-select>
    <v-select :items="['get from OSM']" label="tram lines" variant="outlined"
      @update:modelValue="sendTramLineRequest"></v-select>

    <v-select :items="['get from OSM']" label="water" variant="outlined" @update:modelValue="sendwaterRequest"></v-select>

    <v-select :items="['get from OSM']" label="sidewalk" variant="outlined"
      @update:modelValue="sendSideWalkRequest"></v-select>

    <v-select :items="['get from OSM']" label="bike" variant="outlined" @update:modelValue="sendBikeRequest"></v-select>
    <v-select :items="['get from OSM']" label="amenities" variant="outlined"
      @update:modelValue="getAmenitiesFromOsm"></v-select>
    <v-select :items="['get from OSM']" label="pedestrian area" variant="outlined"
      @update:modelValue="sendPedestrianAreaRequest"></v-select>
    <v-select :items="['calculate']" label="zebraCrossings" variant="outlined"
      @update:modelValue="sendZebraCrossingRequest"></v-select>

    <v-select :items="['get from OSM']" label="rails" variant="outlined"
      @update:modelValue="sendRailsRequest"></v-select>

    <v-alert type="success" v-if="store.state.aoi.dataIsLoaded">
      stored
    </v-alert>
    <v-alert type="info" v-if="store.state.aoi.dataIsLoading">
      getting data...
    </v-alert>
  </v-col>
  <v-col v-show="showUITemp" cols="6" md="3" style="position:absolute; left: 0; bottom:110px; z-index:999; width:800px">
    <div id="console"></div>

  </v-col>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { ref, computed, watch } from "vue";
import {
  clearCache,
  deleteComments,
  getbuildingsFromOSM,
  storeGreeneryFromOSM,
  getTreesFromOSM,
  getDrivingLaneFromOSM,
  getTrafficLightsFromOSM,
  getTramLineFromOSM,
  getWaterFromOSM,
  getSideWalkFromOSM,
  getBikeFromOSM,
  getQuestsFulfillmentFromDB,
  getAmenitiesFromOSM,
  getPedestrianAreaFromOSM,
  getRailsFromOSM
} from "../service/backend.service";
import { HTTP } from "@/utils/http-common";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import type { IControl } from "mapbox-gl";
import * as turf from '@turf/turf';

const store = useStore();
const emit = defineEmits(["getMapOrientation", "addDrawControl"])
const projectSetupInfo = ref<ProjectInformation>({
  'project_id': '',
  'project_name': '',
  'bbox': undefined,
  'project_type': '',
  'project_goal': ''
})
const projectSetupBboxString = ref<string>()
const newProjectJson = ref<ProjectInformation>()
const apiKey = ref<string>()
const showProjectInit = ref<boolean>(false)
const showUITemp = ref<boolean>(true)
const props = defineProps(['drawnPolygon'])


let OSMTrafficSignalSaved = ref(false)
let OSMDrivingLanesSaved = ref(false)
let OSMSidewalkSaved = ref(false)
let OSMBikeLanesSaved = ref(false)
watch(props, function () {
  const bbox = turf.bbox(props.drawnPolygon);
  const box: Bbox = {
    xmin: bbox[0],
    ymin: bbox[1],
    xmax: bbox[2],
    ymax: bbox[3]
  }
  projectSetupBboxString.value = JSON.stringify(box)
  showUITemp.value = true
  showProjectInit.value = true
})
const getBbox = () => {
  showUITemp.value = false
  const draw: IControl = new MapboxDraw({
    displayControlsDefault: false,
    controls: {
      polygon: true
    },
    defaultMode: 'draw_polygon',
  });

  emit("addDrawControl", draw)
}

const closeWindow = () => {
  showProjectInit.value = false
}
const clearServerCache = async () => {
  const result = await clearCache()
  console.log(result.data)

}

const ShoQuestsFulfillment = async () => {
  let message = getQuestsFulfillmentFromDB(store.state.aoi.projectId, store.state.aoi.userId)
  console.log(message)
}

// drops the comments of the current project
const dropCommentData = async () => {
  // projectId
  let thisProjectId = store.state.aoi.projectId;
  let question = "Do you want to delete the comments of project: " + thisProjectId + "?";
  let deleteCommentsAnswer = confirm(question);
  if (deleteCommentsAnswer === true) {
    deleteComments(thisProjectId)
  }
};
interface ProjectInformation {
  project_id: string;
  project_name: string;
  bbox: Bbox | undefined;
  project_type: string;
  project_goal: string;
}
interface Bbox {
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
}
const setupNewProject = async () => {
  let data
  if (!newProjectJson.value) {
    data = projectSetupInfo.value
    const parsedBboxValue = JSON.parse(projectSetupBboxString.value!);
    data.bbox = {
      xmin: parsedBboxValue.xmin,
      ymin: parsedBboxValue.ymin,
      xmax: parsedBboxValue.xmax,
      ymax: parsedBboxValue.ymax,
    };
  }
  else {
    data = newProjectJson.value
  }
  console.log(data)
  await HTTP.post('setup_new_project', data, {
    headers: {
      'X-API-KEY': apiKey.value!,
    }
  })
}
const logMessage = (message: string) => {
  const consoleElement = document.getElementById('console');
  console.log(message);
  consoleElement!.innerHTML += message + '<br>';
};
const loadAllPoiFeaturesFromOSMall1 = async () => {
  logMessage('starting loadAllPoiFeaturesFromOSM...');
  let startTime = performance.now();

  await logAndExecute('sendBuildingRequest', sendBuildingRequest);
  await logAndExecute('sendGreeneryRequest', sendGreeneryRequest);
  await logAndExecute('sendTreeRequest', sendTreeRequest);
  await logAndExecute('sendDrivingLaneRequest', sendDrivingLaneRequest);
  await logAndExecute('sendTrafficSignalRequest', sendTrafficSignalRequest);
  await logAndExecute('sendTramLineRequest', sendTramLineRequest);
  await logAndExecute('sendwaterRequest', sendwaterRequest);
  await logAndExecute('sendSideWalkRequest', sendSideWalkRequest);
  await logAndExecute('sendPedestrianAreaRequest', sendPedestrianAreaRequest);
  await logAndExecute('getAmenitiesFromOsm', getAmenitiesFromOsm);
  await logAndExecute('sendBikeRequest', sendBikeRequest);

  let endTime = performance.now();
  logMessage(`loadAllPoiFeaturesFromOSM took ${Math.ceil((endTime - startTime) / 1000)} seconds`);
};

const logAndExecute = async (funcName: string, func: () => Promise<void>) => {
  logMessage(`starting ${funcName}...`);
  await func();
  logMessage(`${funcName} finished`);
}

const loadAllPoiFeaturesFromOSMall = async () => {

  const requests = [
    sendBuildingRequest(),
    sendGreeneryRequest(),
    sendTreeRequest(),
    sendDrivingLaneRequest(),
    sendTrafficSignalRequest(),
    sendTramLineRequest(),
    sendwaterRequest(),
    sendSideWalkRequest(),
    sendPedestrianAreaRequest(),
    getAmenitiesFromOsm(),
    sendRailsRequest(),
    sendBikeRequest()
  ];

  logMessage('starting loadAllPoiFeaturesFromOSM...');
  let startTime = performance.now();
  await Promise.all(requests);
  let endTime = performance.now();
  logMessage(`loadAllPoiFeaturesFromOSM took ${Math.ceil((endTime - startTime) / 1000)} seconds`);
};

const sendZebraCrossingBool = computed(() => {
  return {
    OSMTrafficSignalSaved: OSMTrafficSignalSaved.value,
    OSMDrivingLanesSaved: OSMDrivingLanesSaved.value,
    OSMSidewalkSaved: OSMSidewalkSaved.value,
    OSMBikeLanesSaved: OSMBikeLanesSaved.value
  }
})

watch(sendZebraCrossingBool, async function () {
  if (
    sendZebraCrossingBool.value.OSMTrafficSignalSaved == true
    && sendZebraCrossingBool.value.OSMDrivingLanesSaved == true
    && sendZebraCrossingBool.value.OSMSidewalkSaved == true
    && sendZebraCrossingBool.value.OSMBikeLanesSaved == true

  ) {
    const consoleElement = document.getElementById('console');
    // Log a message and append it to the console element
    const logMessage = (message: string) => {
      console.log(message);
      consoleElement!.innerHTML += message + '<br>';
    };
    logMessage('generate-zebra-crossing...');
    let startTime = performance.now();
    await sendZebraCrossingRequest();
    let endTime = performance.now();
    logMessage(`generate-zebra-crossing took ${Math.ceil((endTime - startTime) / 1000)} seconds`);
    logMessage(`ALL THE DATA FOR THIS AOI HAS BEEN LOADED!`);
  }
})
const sendZebraCrossingRequest = async () => {

  await HTTP.post("generate-zebra-crossing-table", {
    projectId: store.state.aoi.projectSpecification.project_id,
  })
  logMessage('Zebra done!')

}

const sendBuildingRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getbuildingsFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Buildings done!')
}
const sendGreeneryRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await storeGreeneryFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.usedTagsForGreenery,
    store.state.aoi.projectSpecification.project_id
  );
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Greenery done!')
}
const sendTreeRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getTreesFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Trees done!')
}
const sendDrivingLaneRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getDrivingLaneFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  OSMDrivingLanesSaved.value = true
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Streets done!')
}
const sendTrafficSignalRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getTrafficLightsFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  OSMTrafficSignalSaved.value = true
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Trafficlights done!')
};
const sendwaterRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getWaterFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  logMessage('Water done!')
};

const sendTramLineRequest = async () => {


  store.dispatch("aoi/setDataIsLoading");
  await getTramLineFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Tramlines done!')
};

const sendSideWalkRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getSideWalkFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  OSMSidewalkSaved.value = true
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Pedestrian walking done!')


}
const sendBikeRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");
  await getBikeFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  OSMBikeLanesSaved.value = true
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Bikelanes done!')
}
const getAmenitiesFromOsm = async () => {
  store.dispatch("aoi/setDataIsLoading");
  await getAmenitiesFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Amenities done!')
}
const sendPedestrianAreaRequest = async () => {

  store.dispatch("aoi/setDataIsLoading");

  await getPedestrianAreaFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  );
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Pedestrian areas done!')
}

const sendRailsRequest = async() => {

  store.dispatch("aoi/setDataIsLoading");

  await getRailsFromOSM(
    store.state.aoi.projectSpecification.bbox,
    store.state.aoi.projectSpecification.project_id
  )
  store.dispatch("aoi/setDataIsLoaded");
  logMessage('Train rails done!')
}
</script>
<style scoped>
.v-btn {
  min-width: fit-content;
}

.v-input--density-default {
  --v-input-control-height: 33px;
  --v-input-padding-top: 3px;
}

.card-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  z-index: 1000;
}

.card {
  width: 100%;
  max-width: 500px;
  padding: 20px;
  border-radius: 8px;
  background-color: #ffffff;
  box-sizing: border-box;
  margin: 20px;
  margin-top: 40px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}

.card-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: bold;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.button-container {
  display: flex;
  justify-content: center;
}

.button-container button {
  background-color: #41b883;
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.button-container button:hover {
  background-color: #2a7b57;
}

.close-button {
  position: absolute;
  top: 0;
  right: 0;
}

.bounding-box-container {
  display: flex;
  align-items: flex-end;
}

.bounding-box-input {
  width: 100%;
}
</style>
