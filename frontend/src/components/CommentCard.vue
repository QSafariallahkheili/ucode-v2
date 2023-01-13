<template>
    <v-card
        elevation="3"
        :style="{'--borderColor': props.color?props.color: '#ffffff'}"
    >
        <div @click="() => {isExtended = !isExtended}">
            <div class="time-text text-body-2 text-disabled">{{getRelativeTime(props.created_at)}}</div>
            <div :id="props.id" :class="isExtended?'comment-text text-body-1 is-extended':'comment-text text-body-1'">{{props.comment}}</div>
            <div class="text-body-2 text-disabled show-more">{{contentIsOverflowing && !isExtended?'mehr Anzeigen':''}}</div>
        </div>
        <div class="action-area">
            <v-chip v-if="props.user_id === userId" variant="elevated" size="small" color="primary" >Mein</v-chip>
            <v-chip v-if="props.user_id === userId" variant="text" size="small" append-icon="mdi-thumb-up-outline">{{ props.likes }}</v-chip>
            <v-chip v-if="props.user_id === userId" variant="text" size="small" append-icon="mdi-thumb-down-outline" class="last-chip">{{ props.dislikes }}</v-chip>
            <v-btn
                v-if="(props.user_id === userId && (likes === 0 && dislikes === 0) && false)"
                class="btn-end"
                variant="plain"
                size="small"
                icon="mdi-pencil"
            ></v-btn>
            <v-btn
                v-if="props.user_id === userId"
                class="btn-end"
                variant="plain"
                size="small"
                icon="mdi-delete"
                @click="deleteComment(props.id)"
            ></v-btn> 

            <v-btn-toggle
                v-if="props.user_id !== userId"
                v-model="voting_status"
                variant="text"
                color="secondary"
                rounded="xl"
                class="reaction"
            >
                <v-btn value="like" class="reaction-btn" @click="like">
                    <v-icon start>
                        {{voting_status === "like"?'mdi-thumb-up':'mdi-thumb-up-outline'}}
                    </v-icon>
                    {{ voting_status !== undefined? voting_status === 'like'? likes+1 : likes : '' }}
                </v-btn>
                <v-divider vertical/>
                <v-btn value="dislike" class="reaction-btn" @click="dislike">
                    {{ voting_status !== undefined? voting_status === 'dislike'? dislikes+1 : dislikes : ''}}
                    <v-icon end>
                        {{voting_status === "dislike"?'mdi-thumb-down':'mdi-thumb-down-outline'}}
                    </v-icon>

                </v-btn>
            </v-btn-toggle>
        </div>
    </v-card>
</template>

<script setup>
import { useStore } from "vuex";
import { ref, onMounted } from 'vue';
import { HTTP } from "@/utils/http-common.js";

const store = useStore(); 
const userId = store.state.aoi.userId;
const emit = defineEmits(["deleteComment"]);

const props = defineProps({
    id: {
        type: Number,
        default: undefined
    },created_at: {
        type: String,
        default: "2022-01-01T00:00:00.000000+00:00"
    },
    comment: {
        type: String,
        default: "Kommentar"
    },
    user_id: {
        type: String,
        default: "anonymous"
    },
    likes: {
        type: Number,
        default: 0
    },
    dislikes: {
        type: Number,
        default: 0
    },
    voting_status: {
        type: String,
        default: undefined
    },
    color: {
        type: String,
        default: "#FFFFFF"
    }
})
let voting_status = ref(props.voting_status==="undefined"?undefined:props.voting_status)
let likes = ref(voting_status.value!=='like' || props.user_id === userId?props.likes:props.likes-1)
let dislikes = ref(voting_status.value!=='dislike' || props.user_id === userId?props.dislikes:props.dislikes-1)
let borderColor =  ref('red')
const isExtended = ref(false)
const contentIsOverflowing = ref(false)

const getRelativeTime = (timestamp) => {
    let today = new Date();
    var msPerMinute = 60 * 1000;
    var msPerHour = msPerMinute * 60;
    var msPerDay = msPerHour * 24;
    var msPerMonth = msPerDay * 30;
    var msPerYear = msPerDay * 365;

    var elapsed = today - new Date(timestamp);

    if (elapsed < msPerMinute) {
        let ending = Math.round(elapsed/1000) === 1?' Sekunde':' Sekunden'
        return 'vor ' + Math.round(elapsed/1000) + ending;  
    }

    else if (elapsed < msPerHour) {
        let ending = Math.round(elapsed/msPerMinute) === 1?' Minute':' Minuten'
        return 'vor ' + Math.round(elapsed/msPerMinute) +ending; 
    }

    else if (elapsed < msPerDay ) {
        let ending = Math.round(elapsed/msPerHour) === 1?' Stunde':' Stunden'
        return 'vor ' + Math.round(elapsed/msPerHour) +ending; 
    }

    else if (elapsed < msPerMonth) {
        let ending = Math.round(elapsed/msPerDay) === 1?' Tag':' Tagen'
        return 'vor ' + Math.round(elapsed/msPerDay) +ending;  
    }

    else if (elapsed < msPerYear) {
        let ending = Math.round(elapsed/msPerMonth) === 1?' Monat':' Monate'
        return 'vor ' + Math.round(elapsed/msPerMonth) +ending;     
    }

    else {
        let ending = Math.round(elapsed/msPerYear) === 1?' Jahr':' Jahren'
        return 'vor ' + Math.round(elapsed/msPerYear) +ending;    
    }
}

const like = async () => {
    const response = await HTTP.get("update-voting-status",{
    params: {
        commentId: props.id,
        userId: userId,
        action: "like"
    }
    })
    // console.log(response)
}

const dislike = async () => {
    const response = await HTTP.get("update-voting-status",{
    params: {
        commentId: props.id,
        userId: userId,
        action: "dislike"
    }
    })
    // console.log(response)
}

const deleteComment = (id)=>{
    emit("deleteComment", id)
}

onMounted(() => {
    const el = document.getElementById(props.id)
    contentIsOverflowing.value = el.offsetHeight < el.scrollHeight?true:false
})
</script>

<style scoped>

.v-card{
    margin: 1.5rem 0rem;
    margin-left: 50%;
    padding: 1.5rem;
    transform: translateX(-50%);
    width: calc(100% - 3rem) !important;
    border-radius: 18px;
}
.time-text{
    margin-bottom: 0.5rem;
}

.comment-text{
    min-height: 4.5rem;
    max-height: 4.5rem;
    white-space: pre-line;
    overflow: hidden;
    transition: max-height 0.3s ease-in-out;
    
}
.is-extended{
    max-height: 20rem;
    
}

.show-more{
    min-height: 20px;
}
.action-area{
    margin-top: 1rem;
    display: flex;
    justify-content: flex-end;
    align-items: center;
}
.v-chip{
    margin: 0rem 0.5rem 0rem 0rem;
}

.last-chip{
    margin: 0rem auto 0rem -10px !important;
}
.btn-end{
    font-size: 1rem;
    margin-left: 1rem;
}
.reaction{
    background: rgb(0,0,0,0.02) !important;
}
.reaction-btn{
    color: rgb(0,0,0,0.55)
}
.v-divider{
    height: 1rem;
}
.v-card:after {
  content: '';
  position: absolute;
  left: -2px;
  top: 25%;
  height: 50%;
  border-left: 10px solid;
  border-left-color: var(--borderColor);
  border-radius: 4px;
 
}
</style>