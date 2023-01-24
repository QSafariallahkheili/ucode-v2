<template>
    <div class="comment-gallery-wrapper">
       
        <DeletingDialog
            v-if="(commentsAreLoaded && props.show)"
           :deleteDialog="deleteDialog"
           @cnacelDeleteDialog="cnacelDeleteDialog"
           @confirmDeleteCommentDialog="confirmDeleteCommentDialog"
        />
        
        <transition name="card">
            <div v-if="(commentsAreLoaded && props.show && mapView==false)" className="comment-list"> 
                <CommentSortAndFilter @sortComment="sortComment" @filterComment="filterComment" :bottomPositionSortFilter="bottomPositionSortFilter"/>
                <div>
                    <CommentCard 
                        v-for="comment in filteredCommentList"
                        :id="comment.properties.id" 
                        :created_at="comment.properties.created_at"
                        :comment="comment.properties.comment"
                        :user_id="comment.properties.user_id"
                        :likes="comment.properties.likes"
                        :dislikes="comment.properties.dislikes"
                        :voting_status="comment.properties.voting_status"
                        :color="comment.properties.color"
                        :key="comment.id"
                        @deleteComment="deleteComment"
                    />
                </div>
                
                <v-btn @click="setMapCommentView(); changeCommentSortAndFilterUIPosition(); getCommentsFromDB()" v-if="mapView==false" size="large" icon class="map-comment-view-toggle">
                    <v-icon>mdi-map-outline</v-icon>
                </v-btn>
            </div>
        </transition>
        <transition  name="fade">
            <div v-if="props.show && mapView==false" className="backdrop" >
                <div v-if="(!commentsAreLoaded && props.show)" class="comment-list">
                    <CardSkeleton v-for="index in 4" :key="index"></CardSkeleton>
                </div>
            </div>
        </transition>
        <div v-if="props.show && mapView==true" style="margin-bottom:10px; z-index: 9999; position: absolute; bottom: 340px; right: 1.5rem">
                <v-btn @click="setMapCommentView(); changeCommentSortAndFilterUIPosition(); "  size="large" icon class="comment-view-toggle">
                    <v-icon>mdi-format-list-bulleted</v-icon>
                </v-btn>
        </div>
        <CommentSortAndFilter v-if="props.show && mapView==true" @sortComment="sortComment" @filterComment="filterComment" :bottomPositionSortFilter="bottomPositionSortFilter"/>
        <div class="map-card" v-if="props.show && mapView==true">
            
            

            <div class="set-margin" v-for="comment in filteredCommentList" :key="comment.properties.id"  >

                <CommentCard 
                    :id="comment.properties.id" 
                    :created_at="comment.properties.created_at"
                    :comment="comment.properties.comment"
                    :user_id="comment.properties.user_id"
                    :likes="comment.properties.likes"
                    :dislikes="comment.properties.dislikes"
                    :voting_status="comment.properties.voting_status"
                    :color="comment.properties.color"
                    :key="comment.properties.id"
                    @deleteComment="deleteComment"
                    @mouseenter="mouseEnterOnComment(comment.properties.id)"
            />
            </div>
            
        </div>
    </div>
</template>

<script setup>
    import { onMounted, ref, watch, computed } from 'vue';
    import { useStore } from "vuex";
    import { getFilteredCommentsFromDB } from "../service/backend.service";
    import CardSkeleton from "@/components/CardSkeleton.vue";
    import CommentCard from "@/components/CommentCard.vue"
    import DeletingDialog from "@/components/DeletingDialog.vue"
    import CommentSortAndFilter from "@/components/CommentSortAndFilter.vue"
    import { HTTP } from "@/utils/http-common.js";
    import { getCommentsDataFromDB } from "../service/backend.service"; 


    const store = useStore(); 
    const emit = defineEmits(["deleteQuestCommentFromSource", "scaleUpComment", "toggleCommentLayerVisibility", "updateCommentSource", "addImage"]);
    const projectId = store.state.aoi.projectSpecification.project_id;
    const userId = store.state.aoi.userId;
    let deleteDialog = ref(false)
    let deleteCommentId = ref()
    let filterText = ref()
    let mapView = ref(false)
    const props = defineProps({
        show: {
            type: Boolean,
            default: false
        }
    })

    if(props.show){
        sendCommentRequest()
    }

    let commentList = ref([])
    let commentsAreLoaded = ref(false)
    let bottomPositionSortFilter = ref('')
    
    const delay = (time) => {
        return new Promise(resolve => setTimeout(resolve, time));
    }

    const sendCommentRequest = async () => {
        commentsAreLoaded.value = false;
        let response = []
        let myComments = []
        let otherComments = []
        var start = await performance.now();

        const commentData = await getFilteredCommentsFromDB(projectId, userId)
        response = commentData.props.data
        response.forEach(item => {
            item.properties.user_id !== userId?otherComments.push(item):myComments.push(item);
        })

        myComments = myComments.sort((a,b)=> new Date(b.properties.created_at).getTime() - new Date(a.properties.created_at).getTime())
        otherComments = otherComments.sort((a,b)=> new Date(b.properties.created_at).getTime() - new Date(a.properties.created_at).getTime())

        commentList.value = myComments.concat(otherComments);
        // console.log(commentList.value)

        var loadingTime = performance.now() - start
        if(loadingTime - start < 300){
            await delay(300 - loadingTime)
        }
        commentsAreLoaded.value = true; 
    }
    const deleteComment = (id)=>{
        deleteCommentId.value = id
        deleteDialog.value = true
    }
    const cnacelDeleteDialog = ()=>{
        deleteDialog.value = false
    }
    const confirmDeleteCommentDialog = async()=>{
        deleteDialog.value = false
        let commentInstance = null
        
        commentInstance = commentList.value.map(comment =>comment.properties.id).indexOf(deleteCommentId.value)
        
        for (var i = 0; i < commentList.value.length; i++){
            if (commentList.value[i].properties.id == deleteCommentId.value){
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
        
        const response = await HTTP.post("delete-comment-by-id",{
            commentId: deleteCommentId.value,
        })
        emit("deleteQuestCommentFromSource", store.state.comment.deletedComments)
        store.state.quests.questList[response.data].fulfillment--
    }

    const sortComment = (sortOption) => {
        if (sortOption == "neuste zuerst"){
            commentList.value = commentList.value.sort((a,b)=> new Date(b.properties.created_at).getTime() - new Date(a.properties.created_at).getTime())
        }
        else if (sortOption == "älteste zuerst"){
            commentList.value = commentList.value.sort((a,b)=> new Date(a.properties.created_at).getTime() - new Date(b.properties.created_at).getTime())
        }
        else if (sortOption == "längste zuerst"){
            commentList.value = commentList.value.sort((a,b)=> (b.properties.comment?.length) - (a.properties.comment?.length))
        }
        else if (sortOption == "kürzeste zuerst"){
            commentList.value = commentList.value.sort((a,b)=> (a.properties.comment?.length) - (b.properties.comment?.length))
        }
        else if (sortOption == "beliebte zuerst"){
            commentList.value = commentList.value.sort((a,b)=> (b.properties.likes) - (a.properties.likes))
        }
        else if (sortOption == "unbeliebte zuerst"){
            commentList.value = commentList.value.sort((a,b)=> (b.properties.dislikes) - (a.properties.dislikes))
        }

    }

    const filterComment = (filterOption) => {
        filterText.value = filterOption
    }

    const filteredCommentList = computed( () => {
        let filter = filterText.value
        if (!filter) return commentList.value
        else if (filter.filterType=="meine"){
            return commentList.value.filter( f => f.properties.user_id == filter.filterValue )
        }
        else if (filter.filterType=='planningIdeas'){
            return commentList.value.filter( f => f.properties.route_id == filter.filterValue )
        }
       
    })


    const changeCommentSortAndFilterUIPosition = () => {
       if(mapView.value == true){
            bottomPositionSortFilter.value = "50px"
       }
       else {
            bottomPositionSortFilter.value = ""
       }
        
    }
    const setMapCommentView = () => {
        mapView.value = ! mapView.value
        
    }

    const getCommentsFromDB = async() => {
        let allComments = { type: "FeatureCollection", features: [] }
        for (let f of filteredCommentList.value){
            allComments.features.push(f)
        }
        
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
                'icon-offset': [65, 50],
                'icon-anchor': "bottom",
                'icon-allow-overlap': true,
            }
        }
        store.commit("map/addSource",commentSourceLayer)
        emit('addImage', 'comment.png')
        store.commit("map/addLayer",CommentLayer)
        //emit('addComment', commentSourceLayer, CommentLayer)
        
        
    }

    const mouseEnterOnComment = (HoveredCommentId) => {
        emit('scaleUpComment', HoveredCommentId)
        
    }
   
    onMounted(() => {
        sendCommentRequest();
    })

    watch(props, function () {
        if (props.show){
            sendCommentRequest();
        }
        
    })

    const compoundProperty = computed( () => {
        return {mapview: mapView.value, commentshow: props.show}
       
    })

    watch(compoundProperty, function() { 

        if (compoundProperty.value.mapview==true && compoundProperty.value.commentshow==true){
            emit('toggleCommentLayerVisibility', 'allComments', 'visible')
        }
        else {
            emit('toggleCommentLayerVisibility', 'allComments', 'none')
        }
        
    })

    watch(filteredCommentList, function () {
       if (compoundProperty.value.mapview==true && compoundProperty.value.commentshow==true){
            let allComments = { type: "FeatureCollection", features: [] }
            for (let f of filteredCommentList.value){
                allComments.features.push(f)
            }
            emit('updateCommentSource', { id: 'allComments', geojson: {data: allComments} })
        }
    })
    
    
</script>

<style scoped>
.comment-gallery-wrapper{
    width: 100%;
}
.comment-list{
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
.backdrop{
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
.comment-list.v-card{
    margin: 1.5rem 0rem;
    margin-left: 50%;
    padding: 1.5rem;
    transform: translateX(-50%);
    width: calc(100% - 3rem) !important;
    border-radius: 18px;
}
.map-card {
    padding:0 1.5rem 0 1.5rem !important;
    position: fixed;
    bottom: 110px;
    z-index: 1100;
    max-width: 100%;
    display: flex;
    overflow-x: scroll;
}
.map-card::-webkit-scrollbar {
  display: none;
}
.map-card .v-card{
    margin-top: 0  !important;
    margin-bottom: 0  !important;
    border-radius: 18px;
    width: calc(100vw - 8rem) !important;
    top:0 !important
}

.map-card .set-margin{
    margin-right: 1.5rem ;
    margin-bottom: 0;
   
}
/* Animation */
/* Card      */
 .card-leave-active {
    opacity: 1;
}

.card-leave-to{
    opacity: 0;
}

/* Backdrop */
.fade-enter-active{
    opacity: 0;
    transition: opacity 0.2s linear;
}

.fade-enter-to{
    opacity: 1;
}

 .fade-leave-active {
    opacity: 1;
    transition: opacity 0.3s linear;
}

.fade-leave-to{
    opacity: 0;
}

.map-comment-view-toggle{
    z-index: 9999;
    position: fixed;
    bottom: 60px;
    right:1.5rem;
    scrollbar-width: none !important; 

}
</style>