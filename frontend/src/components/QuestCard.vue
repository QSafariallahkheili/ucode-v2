<template >
    <v-card elevation="5">
        <transition name="fade">
            <div v-if="finishCard" class="backdrop">
                <Vue3Lottie class="animation" :animationData="SuccessJSON" :height="200" :width="200" :loop="false" :delay="900"/>
            </div>
        </transition>
        <div class="text-body-1 font-weight-bold">{{ props.title }}</div>
        <div class="text-body-1 quest-description">{{ props.description }}</div>
        <QuestProgressbar :fulfillment="props.fulfillment" :goal="props.goal"/>   
    </v-card>
</template>

<script lang="ts" setup>
import QuestProgressbar from "@/components/QuestProgressbar.vue";
import { ref, watch } from 'vue';
import { useStore } from "vuex";
import { Vue3Lottie } from 'vue3-lottie'
import 'vue3-lottie/dist/style.css'
import SuccessJSON from '@/../src/animations/quest_completed.json'

const store = useStore();

const props = defineProps({
    title: {
        type: String,
        default: "Title"
    },
    description: {
        type: String,
        default: "short description"
    },
    fulfillment: {
        type: Number,
        default: 0
    },
    goal: {
        type: Number,
        default: 3
    }
})
const finishCard = ref(false)
let lastFullfilment = props.fulfillment;

const emit = defineEmits(["allQuestsCompleted"])

const areAllQuestCompleted = ():Boolean => {
    for(const quest in store.state.quests.questList){
        if(store.state.quests.questList[quest].fulfillment < store.state.quests.questList[quest].goal ){
            return false
        }
    }
    return true
}

watch(props, function () {
    let questCount = 0;
    if(props.fulfillment===props.goal && lastFullfilment < props.fulfillment){
        if(areAllQuestCompleted()){
            emit('allQuestsCompleted')
        } 
        else {
            finishCard.value = true;
            setTimeout(() => {
                finishCard.value = false;
                for (const q in store.state.quests.questList) {questCount++}

                if(store.state.quests.current_order_id < questCount-1)
                    store.state.quests.current_order_id++
            }, 3200);
        }
    }  
    lastFullfilment = props.fulfillment;
})
</script>

<style scoped>
.v-card{
    margin: 1rem 1rem;
    padding: 1.5rem;
    border-radius: 18px;
}
.quest-description{
    min-height: 4.5rem;
    max-height: 4.5rem;
    font-size: 14px !important;
}
.backdrop{
    position: absolute;
    z-index: 1000;
    display:flex;
    justify-content: center;
    align-items: center;
    background: rgb(255,255,255,0.4);
    width: 100%;
    height: 100%;
    margin-top: -1.5rem;
    margin-left: -1.5rem;
}

.animation{
    z-index: 1000;
}

/* Animation */
.fade-enter-active{
    opacity: 0;
    transition: opacity 0.2s;
    transition-delay: 700ms;
}

.fade-enter-to{
    opacity: 1;
}

 .fade-leave-active {
    opacity: 1;
    transition: opacity 0.2s;
    transition-delay: 600ms;
}

.fade-leave-to{
    opacity: 0;
} 
</style>