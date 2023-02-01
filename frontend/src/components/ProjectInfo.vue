<template>
    <div class="projectInfo-container">
        <v-card v-if="props.show" flat rounded="5" style="border-radius: 18px 18px 0px 0px">
            <div class="projectInfo-headline text-h6 font-weight-bold text-center"> Über das Projekt </div>
            <div class="projectInfo-content">
                <div class="v-item-group" v-for="n in sectionsLength" :value="n" :key="n">
                    <div class="text-body-1 font-weight-bold info-sub-headline">{{ Object.keys(sections)[n - 1] }}</div>
                    <div class="text-body-2 info-text" v-html="Object.values(sections)[n - 1]"></div>
                </div>
            </div>
        </v-card>
        <div v-if="props.show" class="backdrop"></div>
    </div>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { reactive, ref } from "vue";
const store = useStore();
let sections = reactive(store.state.aoi.projectInformation)
let sectionsLength = ref(Object.keys(sections).length)

const props = defineProps({
    show: {
        type: Boolean,
        default: false
    }
})

</script>

<style scoped>
.projectInfo-container {
    z-index: 1001;
    width: 100%;
    margin-bottom: 0px;
    scrollbar-width: none !important;
    display: flex;
    flex-direction: column-reverse;
}

.projectInfo-headline {
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
}

.projectInfo-content::-webkit-scrollbar {
    display: none;
}

.projectInfo-content {
    overflow-y: scroll;
}


.v-card {
    z-index: 1002;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 1.5rem;
    max-height: 95vh;
}

.info-sub-headline {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    max-width: 35rem;
    padding-left: 1rem;
    padding-right: 1rem;
    color: gray
}

.info-text {
    margin-top: 0.5rem;
    max-height: 100%;
    max-width: 35rem;
    overflow-y: scroll;
    padding-left: 1rem;
    padding-right: 1rem;
    margin: auto;
}

.v-item-group {
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    overflow-y: scroll;
}

.backdrop {
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    bottom: 0px;
    background: rgb(0, 0, 0, 0.8);
    z-index: 950;
}
</style>