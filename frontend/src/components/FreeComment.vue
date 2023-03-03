<template>
    <div class="comment-container">
        <v-btn v-show="showCommentButton" id="comment-btn" size="large" height="48px" rounded="pill" color="primary"
            @click="placeComment">
            Kommentieren
        </v-btn>
        <transition name="slide">
            <v-card v-show="props.showCommentDialog" id="card" elevation="20">
                <v-btn @click="cancelComment" icon="mdi-close" variant="plain" id="close-btn"/>
                <p class="font-weight-bold text-body-1 call-to-action" >Platziere deinen Kommentar</p>
                <p v-if="!store.state.quests.selectedRouteId" class="text-body-2 text-medium-emphasis call-to-action" >frei in der Stadt</p>
                <p v-if="store.state.quests.selectedRouteId" class="text-body-2 text-medium-emphasis call-to-action" >an der Route {{store.state.quests.selectedRouteId}}</p>
                <div class="comment-text-area">
                    <v-textarea 
                        id="ta-input"
                        :class="commentText!==''?'show-send-btn':'hide-send-btn'"
                        variant="solo" 
                        label="Kommentar"
                        color="primary"
                        bg-color="rgb(248,248,248)"
                        no-resize
                        auto-grow
                        rows="1"
                        max-rows="4"
                        ref="input"
                        :modelValue="commentText"
                        @update:modelValue="text => commentText = text"
                    />
                    <v-btn @click="saveComment" color="primary" icon="mdi-send-outline" size="x-small" id="send-btn"/>
                </div>
            </v-card>
        </transition>
    </div>
</template>
<script lang="ts" setup>
import { useStore } from 'vuex';
import { HTTP } from '@/utils/http-common';
import { computed, onMounted, reactive, ref, watch } from 'vue';
import type { FeatureCollection } from 'geojson';
import bboxPolygon from "@turf/bbox-polygon"
import booleanIntersects from "@turf/boolean-intersects";
import type { Feature } from '@turf/helpers';
import { Popup } from "maplibre-gl";
import type { Quest } from '@/store/modules/quests';


const store = useStore()
let commentText = ref<string>("")
let isFocused = ref<boolean>(false)
let allMarker = reactive<FeatureCollection>({ type: "FeatureCollection", features: [] })
let taLineCount = ref<number>(1)

const showCommentButton = computed(()=>{
    if(store.state.quests.current_quest_type==2 || !store.state.quests.hasQuests){
        return true
    }
    else{
        return false
    }
})
const commentBtnBottom = computed(()=>{
    if(store.state.ui.planningIdeasLoaded){
        return '8rem'
    }
    else{
        return '5rem'
    }

})
let commentValidationPopup = new Popup({ closeButton: false, closeOnClick: false, offset: [0, -50] })

const props = defineProps({
    showCommentDialog: {
        type: Boolean,
        default: false
    }
})
const emit = defineEmits(["addComment", "hideQuests","closeCommentDialog", "placeComment", "addPopup"])
/*const currentQuestType = computed(() => {
  if (Object.keys(store.state.quests.questList).length === 0) {
  }
  else {
    let quest = store.state.quests.questList
    for (let i in store.state.quests.questList) {
      if (quest[i]["order_id"] == store.state.quests.current_order_id) {
        return quest[i].type
      }
    }
  }
})*/
function cancelComment() {
    // store.commit('freecomment/setMoveComment', false)
    commentText.value = ""
    store.state.freecomment.moveableCommentMarker.remove()

    let card = document.getElementById('card')
    
    card?.classList.remove('expand');
    card?.classList.remove('reduce');

    emit('closeCommentDialog')
}

function placeComment(){
    emit('placeComment')
    emit('hideQuests')
}
function createComment(){
    const coords = store.state.freecomment.moveableCommentMarker.getLngLat()
    let marker = {
        type: "Feature",
        geometry: {
            type: "Point",
            coordinates: [coords.lng, coords.lat]
        }
    }
    //@ts-ignore
    allMarker.features.push(marker)
    let mapsource = {
        id: "ownComments",
        geojson: {
            "type": "geojson",
            "data": allMarker
        }
    }
    let ownCommentLayer = {
        'id': "ownComments",
        'type': 'symbol',
        'source': "ownComments",
        'layout': {
            'icon-image': 'comment.png', // reference the image
            'icon-size': 0.15,
            'icon-offset': [65, 0],
            'icon-anchor': "bottom",
            'icon-allow-overlap': true,
        }
    }
    emit('addComment', mapsource, ownCommentLayer)

}

const saveComment = () => {

    /* check if the position of the comment intersects with the AOI */

    const coords = store.state.freecomment.moveableCommentMarker.getLngLat()
    let marker  = <Feature>{
        type: "Feature",
        geometry: {
            type: "Point",
            coordinates:[coords.lng, coords.lat]
        }
    }
    let bbox = store.state.aoi.projectSpecification.bbox
    let AOIPolygon = <Feature> bboxPolygon([bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax]);
    let intersects = <Boolean> booleanIntersects(AOIPolygon, marker);
    
    if (intersects){
        let quest: Quest = store.state.quests.questList[store.state.quests.current_order_id]
        let questId:number|null;
        if(quest){
            questId = quest.quest_id
            store.state.quests.questList[store.state.quests.current_order_id].fulfillment++
        }
        else{
            questId = null
        }
        store.state.freecomment.moveableCommentMarker.remove()
        createComment()
        const submitComment = () => {
            HTTP
                .post('add-comment', {
                    projectId: store.state.aoi.projectSpecification.project_id,
                    comment: commentText.value,
                    //@ts-ignore
                    position: allMarker.features[allMarker.features.length-1].geometry.coordinates,
                    userId: store.state.aoi.userId,
                    questId: questId,
                    routeId: store.state.quests.selectedRouteId
                })
        }
        submitComment()
        commentText.value = ""
        // store.commit('freecomment/setMoveComment', false)
        emit('closeCommentDialog')
        
    }
    else {

        commentValidationPopup.setLngLat(coords)
        commentValidationPopup.setHTML(`Bitte platziere deinen Kommentar im gekennzeichneten Bereich!`
        )
        emit("addPopup", commentValidationPopup)
        const el = document.getElementsByClassName('maplibregl-popup-tip')[0] as HTMLElement;
        el.style.display="none"
        const popupContent = document.getElementsByClassName('maplibregl-popup-content')[0] as HTMLElement;
        popupContent.style.borderRadius="8px"
        popupContent.style.backgroundColor='#FFA500'
        popupContent.style.color="black"
        popupContent.style.textAlign="center"
        setTimeout(function(){
 	        commentValidationPopup.remove()
        }, 3000);
    }
    
}
/************************************************/
/*   handle Commenting Dialog for IOS, IPadOS   */
/************************************************/
const isIOSorIPadOS = () => {
    var userAgent = navigator.userAgent.toLowerCase();
    if(userAgent.match('iphone' || 'ipad')){
        return true
    } else {
        return false
    }
}
//@ts-ignore
function has_scrollbar(elem)
{
    var clientHeight = elem.clientHeight;
    if(clientHeight < 120){
        return false
    }
    //@ts-ignore
    if (elem.clientHeight < elem.scrollHeight)
        return true
    else
        return false
}

watch(commentText, function () {
    
    let input = document.getElementById('ta-input')
    let card = document.getElementById('card')
    // console.log(has_scrollbar(input))
    
    if(has_scrollbar(input)){
        input?.classList.remove('ta-not-scroll');
        input?.classList.add('ta-scroll')
    } else {
        input?.classList.add('ta-not-scroll');
        input?.classList.remove('ta-scroll')
    }


    if(input && card && isIOSorIPadOS()){
        if(commentText.value !== ''){
            input.onblur = function() {
                card?.classList.remove('expand');
                card?.classList.remove('reduce');
            };
            input.onfocus = function() {
                card?.classList.remove('expand');
                card?.classList.remove('reduce');
            };
        } 
        if (commentText.value === '') {
            input.onblur = function() {
                card?.classList.remove('expand');
                card?.classList.add('reduce');
            };
            input.onfocus = function() {
                card?.classList.remove('reduce');
                card?.classList.add('expand');
            };
        }
       
    }
})

onMounted(() => {
    let input = document.getElementById('ta-input')
    let card = document.getElementById('card')

    if(has_scrollbar(input)){
        input?.classList.remove('ta-not-scroll');
        input?.classList.add('ta-scroll')
    } else {
        input?.classList.add('ta-not-scroll');
        input?.classList.remove('ta-scroll')
    }
    
    if(input && card && isIOSorIPadOS()){
        input.onblur = function() {
            card?.classList.remove('expand');
            card?.classList.add('reduce');
        };

        input.onfocus = function() {
            card?.classList.remove('reduce');
            card?.classList.add('expand');
        };
    } 
})
</script>

<style>
.ta-not-scroll{
    touch-action: none !important;
}

.ta-scroll{
    overscroll-behavior: none !important;
    overflow-y: scroll !important;
}

.expand{
    animation: expand-animation 0.25s ease-in-out 0s 1 forwards !important;
}

.reduce{
    animation: reduce-animation 0.25s ease-in-out 0s 1 forwards !important;
}

@keyframes expand-animation {
    0%   {padding-bottom: 0rem;}
    100% {padding-bottom: 296px;}
}
@keyframes reduce-animation {
    0%   {padding-bottom: 296px;}
    100% {padding-bottom: 0rem;}
}
</style>

<style scoped>
.comment-container {
    display: flex;
    touch-action: none;
    justify-content: center;
    width: 100%;
}

#comment-btn{
    touch-action: none;
    order: -1 !important;
    z-index: 998;
    position: absolute;
    bottom: v-bind(commentBtnBottom)
}
.v-card {
    position: relative;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
    width: 100%;
    z-index: 1005;
    border-radius: 12px 12px 0px 0px;
    margin-bottom: 0px;
    touch-action: none;
}

#close-btn{
    touch-action: none;
    position: relative; 
    margin: 0em 0em 0em auto;
}
.call-to-action{
    text-align: center;
    width: 100%;
    margin-bottom: 0px !important;
}
.comment-text-area{
    touch-action: none;
    display: flex;
    padding: 1em 0em 0em 1em;
}
#send-btn{
    position: relative;
    margin-top: auto;
    margin-bottom: 3em;
    margin-right: 2em;
    margin-left: -3.5rem;
}

.v-textarea{
     margin-right: 1em;
     z-index: 1;
 }

/* Animation */
.slide-enter-active{
    margin-bottom: -25em;
    transition: margin-bottom 0.4s ease-out;
}

.slide-enter-to{
    margin-bottom: 0px;
}

 .slide-leave-active {
    margin-bottom: 0px;
    transition: margin-bottom 0.3s ease-in;
}

.slide-leave-to{
    margin-bottom: -25em;
} 

.show-send-btn{
    scrollbar-width: 0px;
    animation: slide-left 0.2s ease-in-out 0s 1 forwards;
}

@keyframes slide-left {
    0%   {margin-right: 1em;}
    100% {margin-right: 4em;}
}

.hide-send-btn{
    animation: slide-right 0.2s ease-in-out 0s 1 forwards;
}

@keyframes slide-right {
    0%   {margin-right: 4em;}
    100% {margin-right: 1em;}
}
.mapboxgl-popup-anchor-bottom .mapboxgl-popup-tip, .maplibregl-popup-anchor-bottom .maplibregl-popup-tip {
    align-self: center;
    border-bottom: none;
    border-top-color: #fff;
    display: none;
}

</style>