<template>
    <div class="comment-gallery-wrapper">
        <DeletingDialog
            v-if="(commentsAreLoaded && props.show)"
           :deleteDialog="deleteDialog"
           @cnacelDeleteDialog="cnacelDeleteDialog"
           @confirmDeleteCommentDialog="confirmDeleteCommentDialog"
        />
        <transition name="card">
            <div v-if="(commentsAreLoaded && props.show)" className="comment-list"> 
                <CommentCard 
                    v-for="comment in commentList"
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
        </transition>
        <transition  name="fade">
            <div v-if="props.show" className="backdrop">
                <div v-if="(!commentsAreLoaded && props.show)" class="comment-list">
                    <CardSkeleton v-for="index in 4" :key="index"></CardSkeleton>
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup>
    import { onMounted, ref, watch } from 'vue';
    import { useStore } from "vuex";
    import { getFilteredCommentsFromDB } from "../service/backend.service";
    import CardSkeleton from "@/components/CardSkeleton.vue";
    import CommentCard from "@/components/CommentCard.vue"
    import DeletingDialog from "@/components/DeletingDialog.vue"
    import { HTTP } from "@/utils/http-common.js";


    const store = useStore(); 
    const emit = defineEmits(["deleteQuestCommentFromSource"]);
    const projectId = store.state.aoi.projectSpecification.project_id;
    const userId = store.state.aoi.userId;
    let deleteDialog = ref(false)
    let deleteCommentId = ref()

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

    onMounted(() => {
        sendCommentRequest();
    })

    watch(props, function () {
        if (props.show){
            sendCommentRequest();
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
.v-card{
    margin: 1.5rem 0rem;
    margin-left: 50%;
    padding: 1.5rem;
    transform: translateX(-50%);
    width: calc(100% - 3rem) !important;
    border-radius: 18px;
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
</style>