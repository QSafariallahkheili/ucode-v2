<template>
    <div :class="props.show?'quests-completed-wrapper':''" @click="onClick">
        <Vue3Lottie v-if="props.show" id="animation" :animationData="SuccessJSON" :width="auto" :loop="false" :delay="1000"/>
        <transition name="slide">
            <v-card v-if="props.show  && !wasShown" >
                <div class="text-h5 font-weight-bold text-center">Vielen Dank</div>
                <div class="text-h5 font-weight-bold text-center">für deine Beteiligung!</div>
                <v-icon class="success-icon" size="x-large" color="secondary" icon="mdi-party-popper"></v-icon>
                <div class="text-body-2 text-medium-emphasis content">
                    Glückwunsch! Du hast alle Quests erfolgreich abgeschlossen. <br/><br/>
                    Falls du dich weiter beteiligen möchtest, nimm dir jetzt die Zeit und reagiere auf Kommentare von anderer Nutzer:innen.<br/>
                    Gehe dafür in den Tap Diskussionen  
                    <v-icon size="x-small" icon="mdi-comment-text-multiple text-medium-emphasis"></v-icon>
                    !
                </div>
            </v-card>
        </transition>
        <transition name="fade">
            <div v-if="props.show && !wasShown" class="background"></div>
        </transition>
        
    </div>
</template>
<script setup>
import { Vue3Lottie } from 'vue3-lottie'
import 'vue3-lottie/dist/style.css'
import SuccessJSON from '@/../src/animations/all_quests_completed.json'
import { ref } from "vue"

const props = defineProps({
    show: {
        type: Boolean,
        default: false
    }
})
const emit = defineEmits(["allQuestsCompletedWasShown"])
const wasShown = ref(false);

const onClick = () => {
    wasShown.value = true;

    setTimeout(() => {
        emit('allQuestsCompletedWasShown');
        wasShown.value = false;
    }, 500);
    
}

</script>
<style scoped>
.quests-completed-wrapper{
    position: fixed;
    width: 100%;
    height: 100%;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: center;
}
.background{
    position: absolute;
    height: 100%;
    width: 100%;
    background: rgb(0,0,0,0.3);
}
#animation{
    position: fixed;
    height: 100% !important;
    width: 200%;
    z-index: 1101;
}
#animation > svg{
    width: auto !important;
}
.v-card{
    z-index: 1100;
    padding: 2rem;
    border-radius: 18px;
    position: absolute;
    bottom: 0%;
    transition-delay: 1000ms;
    margin: auto 1rem 4.5rem 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.success-icon{
    margin: 2rem 0rem 0.5rem 0rem;
    transform: scale(3);
    height: 72px;
    width: 72px;
}
.content{
    margin: 0rem 1rem;
}

/* Transition */
.fade-enter-active{
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    transition-delay: 800ms;
}

.fade-enter-to{
    opacity: 1;
}

 .fade-leave-active {
    opacity: 1;
    transition: opacity 0.2s ease-in-out;
    transition-delay: 0ms;
}

.fade-leave-to{
    opacity: 0;
}
.slide-enter-active{
    bottom: -50%;
    transition: bottom 0.5s ease-out;
    transition-delay: 800ms;
}

.slide-enter-to{
    bottom: 0%;
}

 .slide-leave-active {
    bottom: 0%;
    transition: bottom 0.3s ease-in;
    transition-delay: 0ms;
}

.slide-leave-to{
    bottom: -50%;
}
</style>
