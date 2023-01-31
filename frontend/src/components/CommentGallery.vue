<template>
    <div class="comment-gallery-wrapper" v-if="props.show">

        <DeletingDialog v-if="(commentsAreLoaded && props.show)" :deleteDialog="deleteDialog"
            @cnacelDeleteDialog="cnacelDeleteDialog" @confirmDeleteCommentDialog="confirmDeleteCommentDialog" />

        <transition name="card">
            <div v-if="(commentsAreLoaded && props.show && mapView == false)" className="comment-list">
                <CommentSortAndFilter @sortComment="sortComment" @multifFilterComment="multifFilterComment"
                    :bottomPositionSortFilter="bottomPositionSortFilter" :activfilterOptions="activfilterOptions" />
                <div>
                    <CommentCard v-for="comment in filteredCommentList" :id="comment.properties.id"
                        :created_at="comment.properties.created_at" :comment="comment.properties.comment"
                        :user_id="comment.properties.user_id" :likes="comment.properties.likes"
                        :dislikes="comment.properties.dislikes" :voting_status="comment.properties.voting_status"
                        :color="comment.properties.color" :key="comment.properties.id" @deleteComment="deleteComment" />
                </div>

                <v-btn @click="setMapCommentView(); changeCommentSortAndFilterUIPosition(); buildCommentLayer()"
                    v-if="mapView == false" size="large" icon class="map-comment-view-toggle">
                    <v-icon>mdi-map-outline</v-icon>
                </v-btn>
            </div>
        </transition>
        <transition name="fade">
            <div v-if="props.show && mapView == false" className="backdrop">
                <div v-if="(!commentsAreLoaded && props.show)" class="comment-list">
                    <CardSkeleton v-for="index in 4" :key="index"></CardSkeleton>
                </div>
            </div>
        </transition>
        <div class="map-comment-container">
            <div v-if="props.show && mapView == true">
                <v-btn @click="setMapCommentView(); changeCommentSortAndFilterUIPosition(); " size="large" icon class="list-comment-view-toggle">
                    <v-icon>mdi-format-list-bulleted</v-icon>
                </v-btn>
            </div>
            <div class="map-card" v-if="props.show && mapView == true">
                <div class="set-margin" v-for="comment in filteredCommentList" :key="comment.properties.id">

                    <CommentCard :id="comment.properties.id" :created_at="comment.properties.created_at"
                        :comment="comment.properties.comment" :user_id="comment.properties.user_id"
                        :likes="comment.properties.likes" :dislikes="comment.properties.dislikes"
                        :voting_status="comment.properties.voting_status" :color="comment.properties.color"
                        :key="comment.properties.id" @deleteComment="deleteComment"
                        @mouseenter="mouseEnterOnComment(comment.properties.id)" :mapView="mapView" />
                </div>
            </div>
        </div>
        <CommentSortAndFilter v-if="props.show && mapView == true" @sortComment="sortComment"
            @multifFilterComment="multifFilterComment" :bottomPositionSortFilter="bottomPositionSortFilter"
            :activfilterOptions="activfilterOptions" />

    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, computed, reactive } from 'vue';
import { useStore } from "vuex";
import { getFilteredCommentsFromDB } from "../service/backend.service";
import CardSkeleton from "@/components/CardSkeleton.vue";
import CommentCard from "@/components/CommentCard.vue"
import DeletingDialog from "@/components/DeletingDialog.vue"
import CommentSortAndFilter from "@/components/CommentSortAndFilter.vue"
import { HTTP } from "@/utils/http-common.js";
import comment from '@/store/modules/comment';
import type { Feature } from '@turf/helpers';
import bbox from "@turf/bbox";

const store = useStore();
const emit = defineEmits(["deleteQuestCommentFromSource", "scaleUpComment", "toggleLayerVisibility", "updateCommentSource", "addImage", "fitBoundsToBBOX"]);
const projectId = store.state.aoi.projectSpecification.project_id;
const userId = store.state.aoi.userId;
let deleteDialog = ref(false)
let deleteCommentId = ref()
let mapView = ref(false)
let commentLayerBuilt = ref(false)
let filterArray = ref<{ isActive: boolean, filterOptions: { filterType: string, filterValue: number | string } }[]>()
let activfilterOptions = ref<{ isActive: boolean, filterOptions: { filterType: string, filterValue: number | string } }[]>([
    { isActive: false, filterOptions: { filterType: 'meine', filterValue: "" } },
    { isActive: false, filterOptions: { filterType: 'planningIdea', filterValue: 1 } },
    { isActive: false, filterOptions: { filterType: 'planningIdea', filterValue: 2 } },
    { isActive: false, filterOptions: { filterType: 'planningIdea', filterValue: 3 } }])
let filteredList = reactive<any[]>([])
const currentSorting = ref<string>("")
const props = defineProps({
    show: {
        type: Boolean,
        default: false
    }
})

let commentList = ref<any[]>([])
let commentsAreLoaded = ref<boolean>(false)
let bottomPositionSortFilter = ref<string>('')
const delay = (time: number) => {
    return new Promise(resolve => setTimeout(resolve, time));
}

const sendCommentRequest = async () => {
    commentsAreLoaded.value = false;
    let response: any[] = []
    let myComments: any[] = []
    let otherComments: any[] = []
    var start = performance.now();

    const commentData = await getFilteredCommentsFromDB(projectId, userId)
    //@ts-ignore
    commentData.features.forEach(item => {
        item.properties.user_id !== userId ? otherComments.push(item) : myComments.push(item);
    })

    myComments = myComments.sort((a, b) => new Date(b.properties.created_at).getTime() - new Date(a.properties.created_at).getTime())
    otherComments = otherComments.sort((a, b) => new Date(b.properties.created_at).getTime() - new Date(a.properties.created_at).getTime())

    commentList.value = myComments.concat(otherComments);
    // console.log(commentList.value)
    var loadingTime = performance.now() - start
    if (loadingTime - start < 300) {
        await delay(300 - loadingTime)
    }
    commentsAreLoaded.value = true;
}
if (props.show) {
    sendCommentRequest()
}

const deleteComment = (id: number) => {
    deleteCommentId.value = id
    deleteDialog.value = true
}
const cnacelDeleteDialog = () => {
    deleteDialog.value = false
}
const confirmDeleteCommentDialog = async () => {
    deleteDialog.value = false
    let commentInstance = null

    commentInstance = commentList.value.map(comment => comment.properties.id).indexOf(deleteCommentId.value)

    for (var i = 0; i < commentList.value.length; i++) {
        if (commentList.value[i].properties.id == deleteCommentId.value) {
            let marker = {
                type: "Feature",
                geometry: {
                    type: "Point",
                    coordinates: commentList.value[i].geometry.coordinates
                }
            }

            store.state.comment.deletedComments.push(marker)
        }
    }
    commentList.value.splice(commentInstance, 1);

    const response = await HTTP.post("delete-comment-by-id", {
        commentId: deleteCommentId.value,
    })
    emit("deleteQuestCommentFromSource", store.state.comment.deletedComments)
    store.state.quests.questList[response.data].fulfillment--
}

const sortComment = (sortOption: string) => {
    currentSorting.value = sortOption
    if (sortOption == "neuste zuerst") {
        filteredList = filteredList.sort((a, b) => new Date(b.properties.created_at).getTime() - new Date(a.properties.created_at).getTime())
    }
    else if (sortOption == "älteste zuerst") {
        filteredList = filteredList.sort((a, b) => new Date(a.properties.created_at).getTime() - new Date(b.properties.created_at).getTime())
    }
    else if (sortOption == "längste zuerst") {
        filteredList = filteredList.sort((a, b) => (b.properties.comment?.length) - (a.properties.comment?.length))
    }
    else if (sortOption == "kürzeste zuerst") {
        filteredList = filteredList.sort((a, b) => (a.properties.comment?.length) - (b.properties.comment?.length))
    }
    else if (sortOption == "beliebte zuerst") {
        filteredList = filteredList.sort((a, b) => (b.properties.likes) - (a.properties.likes))
    }
    else if (sortOption == "unbeliebte zuerst") {
        filteredList = filteredList.sort((a, b) => (b.properties.dislikes) - (a.properties.dislikes))
    }
}

const multifFilterComment = (filterOption: { isActive: boolean, filterOptions: { filterType: string, filterValue: number | string } }[]) => {

    activfilterOptions.value = filterOption
    filterArray.value = activfilterOptions.value
}

const filteredCommentList = computed(() => {
    let filterAr = filterArray.value
    if (!filterAr || filterAr.filter(f => f.isActive == true).length == 0) {
        filteredList = commentList.value
        if (currentSorting.value != "") {
            sortComment(currentSorting.value)
        }
        return filteredList
    }
    else {
        filteredList = []
    }
    filterAr.map(filter => {
        if (!filter.isActive) {
            return
        }
        else {
            let filterOption = filter.filterOptions

            if (!filter) {
                return
            }
            else if (filterOption.filterType == "meine") {
                if (filterOption.filterValue == '') {
                    filterOption.filterValue = store.state.aoi.userId
                }
                if (commentList.value.filter(f => f.properties.user_id == filterOption.filterValue).length > 0) {
                    commentList.value.filter(f => f.properties.user_id == filterOption.filterValue).forEach(comment => {
                        filteredList.push(comment)
                    })
                }
            }
            else if (filterOption.filterType == "planningIdea") {
                if (commentList.value.filter(f => f.properties.route_id == filterOption.filterValue).length > 0) {
                    commentList.value.filter(f => f.properties.route_id == filterOption.filterValue).forEach(comment => {
                        filteredList.push(comment)
                    })
                }
            }
            else if (filterOption.filterType == "quest") {
                if (commentList.value.filter(f => f.properties.quest_id == filterOption.filterValue).length > 0) {
                    commentList.value.filter(f => f.properties.quest_id == filterOption.filterValue).forEach(comment => {
                        filteredList.push(comment)
                    })
                }
            }
            else if (filterOption.filterType == "keyword") {
                if (commentList.value.filter(f => f.properties.comment.split(" ").includes(filterOption.filterValue)).length > 0) {
                    commentList.value.filter(f => f.properties.comment.split(" ").includes(filterOption.filterValue)).forEach(comment => {
                        filteredList.push(comment)
                    })
                }
            }
        }
    })
    //console.log(filteredList)
    // filteredList.length == 0 ? filteredList = commentList.value:undefined
    if (currentSorting.value != "") {
        sortComment(currentSorting.value)
    }
    return filteredList
})

onMounted(() => {
    sendCommentRequest();
})

const changeCommentSortAndFilterUIPosition = () => {
    if (mapView.value == true) {
        bottomPositionSortFilter.value = "56px"
    }
    else {
        bottomPositionSortFilter.value = ""
    }

}
const setMapCommentView = () => {
    mapView.value = !mapView.value
}

const buildCommentLayer = async () => {

    let allComments: { type: string, features: Feature[] } = { type: "FeatureCollection", features: [] }

    allComments.features=filteredCommentList.value
    const allCommentsBBOX = bbox(allComments)
    if (allComments.features.length){
        emit("fitBoundsToBBOX", allCommentsBBOX)
    }
    if (commentLayerBuilt.value==false){
        let commentSourceLayer = {
            id: "allComments",
            geojson: {
                "type": "geojson",
                "data": allComments
            }
        }
        let CommentLayer = {
            'id': "allComments",
            'type': 'symbol',
            'source': "allComments",
            'layout': {
                'icon-image': 'comment.png', // reference the image
                'icon-size': 0.15,
                'icon-offset': [65, 0],
                'icon-anchor': "bottom",
                'icon-allow-overlap': true,
            }
        }
        store.commit("map/addSource", commentSourceLayer)
        emit('addImage', 'comment.png')
        store.commit("map/addLayer", CommentLayer)
        commentLayerBuilt.value = true
    }
    else {
        emit('updateCommentSource', { id: 'allComments', geojson: { data: allComments } })
    }

}

const mouseEnterOnComment = (HoveredCommentId: string) => {
    emit('scaleUpComment', HoveredCommentId)

}


watch(props, function () {
    if (props.show) {
        sendCommentRequest();
    }
})

const compoundProperty = computed(() => {
    return { mapview: mapView.value, commentshow: props.show }

})

watch(compoundProperty, function () {

    if (compoundProperty.value.mapview == true && compoundProperty.value.commentshow == true) {
        emit('toggleLayerVisibility', 'allComments', 'visible')
    }
    else {
        emit('toggleLayerVisibility', 'allComments', 'none')
    }

})

watch(filteredCommentList, function () {
    if (compoundProperty.value.mapview == true && compoundProperty.value.commentshow == true) {
        let allComments: { type: string, features: Feature[] } = { type: "FeatureCollection", features: [] }
        allComments.features = filteredCommentList.value

        emit('updateCommentSource', { id: 'allComments', geojson: { data: allComments } })

        const allCommentsBBOX = bbox(allComments)
        if (allComments.features.length){
            emit("fitBoundsToBBOX", allCommentsBBOX)
        }
    }
})


</script>

<style scoped>
.comment-gallery-wrapper {
    width: 100%;
}

.map-comment-container {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    position: relative;
    bottom: 113px;
    z-index: 1105;
}
.list-comment-view-toggle{
    margin: 0 1.5rem 1rem 0
}
.comment-list {
    position: fixed;
    top: 0px;
    width: 100vw;
    height: calc(100% - 56px + 10rem);
    z-index: 1001;
    padding: 0em 0em;
    padding-bottom: 10rem;
    overflow-x: hidden !important;
    overflow-y: scroll !important;
    scrollbar-width: none !important;
}

.backdrop {
    position: fixed;
    top: 0px;
    width: 100vw;
    height: 100%;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    -moz-backdrop-filter: blur(24px);
    -ms-backdrop-filter: blur(24px);
    z-index: 1000;
}

.comment-list::-webkit-scrollbar {
    display: none;
}


.comment-list.v-card {
    margin: 1.5rem 0rem;
    margin-left: 50%;
    padding: 1.5rem;
    transform: translateX(-50%);
    width: calc(100% - 3rem) !important;
    border-radius: 18px;
}

.map-card {
    padding: 0 1rem 1rem 1rem !important;
    position: relative;
    max-width: 100%;
    display: flex;
    align-items: flex-end;
    overflow-x: scroll;
}

.map-card::-webkit-scrollbar {
    display: none;
}

.map-card .v-card {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    border-radius: 18px;
    width: calc(100vw - 3rem) !important;
    top: 0 !important
}

.map-card .set-margin {
    margin-right: 1.5rem;
    margin-bottom: 0;

}

/* Animation */
/* Card      */
.card-leave-active {
    opacity: 1;
}

.card-leave-to {
    opacity: 0;
}

/* Backdrop */
.fade-enter-active {
    opacity: 0;
    transition: opacity 0.2s linear;
}

.fade-enter-to {
    opacity: 1;
}

.fade-leave-active {
    opacity: 1;
    transition: opacity 0.3s linear;
}

.fade-leave-to {
    opacity: 0;
}

.map-comment-view-toggle {
    z-index: 1100;
    position: fixed;
    bottom: 60px;
    right: 1.5rem;
    scrollbar-width: none !important;

}
</style>