<template>
   <div>
    <v-textarea
      solo
      name="input-7-4"
      label="leave a comment"
      :modelValue="commentText"
      @update:modelValue="text => commentText = text"
    ></v-textarea>
    <v-btn
      size="small"
      color="success"
      @click="submitComment"
      :disabled="!commentText"
    >
      Submit
    </v-btn>
        
   </div>

</template>

<script setup>
import {useStore} from "vuex";
import { ref } from 'vue';
const store = useStore();
import { HTTP } from '../utils/http-common';


let commentText = ref("")

const submitComment= ()=>{
  HTTP
  .post('add-comment', {
    comment: commentText.value,
    position: store.state.contribution.commentPosition
  })
  
  store.state.contribution.commentToggle=false
  let marker =  {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [store.state.contribution.commentPosition[0], store.state.contribution.commentPosition[1]]
    }
  }

  if (store.state.contribution.commentGeojson.features.length==0){
    store.state.map.map.addSource('comment', {
      "type": "geojson",
      "data": store.state.contribution.commentGeojson
    })

    store.state.contribution.commentGeojson.features.push(marker)
    store.state.map.map.getSource('comment').setData(store.state.contribution.commentGeojson)

    store.state.map.map.addLayer({
      'id': 'comment',
      'type': 'circle',
      'source': 'comment',
      'paint': {
          'circle-color': 'green',
      }
    }, store.state.aoi.overpassBuildings? "overpass_buildings" : "");

  }
  else{
    store.state.contribution.commentGeojson.features.push(marker)
    store.state.map.map.getSource('comment').setData(store.state.contribution.commentGeojson)
  }

  if (store.state.contribution.commentPopup.isOpen()){
    store.state.contribution.commentPopup.remove()
  }
}
</script>

<style scoped>

</style>