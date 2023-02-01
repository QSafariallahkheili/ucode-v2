<template>
    <div class="intro">
        <v-card flat rounded="5" style="border-radius: 18px 18px 0px 0px">
            <v-window v-model="onboarding" style="width: 100%">
                <v-window-item v-for="n in sectionsLength" :key="`card-${n}`" :value="n">
                    <v-card-actions class="justify-center" style="margin: auto; padding: 0px !important;">
                        <div class="text-body-1 font-weight-bold text-center"> {{ Object.keys(sections)[n - 1] }} </div>
                    </v-card-actions>
                    <div class="text-body-2 intro-text" v-html="Object.values(sections)[n - 1]"></div>
                </v-window-item>
            </v-window>
            <v-card-actions class="justify-space-between">
                <v-item-group v-model="onboarding" class="text-center" mandatory>
                    <v-item v-for="n in sectionsLength" :key="`btn-${n}`" v-slot="{ isSelected, toggle }" :value="n">
                        <v-btn icon="mdi-record" size="small" @click="toggle"
                            :color="isSelected ? 'black' : 'grey'"></v-btn>
                    </v-item>
                </v-item-group>
            </v-card-actions>
            <div class="intro-action-area" v-if="onboarding != 3">
                <v-btn color="secondary" @click="next">
                    Weiter
                </v-btn>
                <v-btn color="grey" variant="plain" class="justify-center align-center" @click="closeIntro"
                    v-show="onboarding != sectionsLength ? true : false">
                    Ich habe es bereits gelesen
                </v-btn>
            </div>
            <div class="intro-action-area" v-if="onboarding == 3">
                <v-btn color="secondary" @click="closeIntro">
                    Auf geht's
                </v-btn>
            </div>
        </v-card>

        <div class="backdrop"></div>
    </div>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { reactive, ref } from "vue";
const store = useStore();
let onboarding = ref(0)
let sections = reactive(store.state.aoi.projectInformation)
let sectionsLength = ref(Object.keys(sections).length)

const next = () => {
    onboarding.value = onboarding.value + 1 > sectionsLength.value
        ? 1
        : onboarding.value + 1
}
const prev = () => {
    onboarding.value = onboarding.value - 1 <= 0
        ? sectionsLength.value
        : onboarding.value - 1
}
const closeIntro = () => {
    store.state.ui.intro = false
}
</script>

<style scoped>
.intro {
    z-index: 1000;
    width: 100%;
}

.section-description {
    overflow: auto
}

.v-card {
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 1.5rem;
}

.intro-text {
    margin-top: 0.5rem;
    min-height: 10rem;
    max-height: 10rem;
    max-width: 35rem;
    overflow-y: scroll;
    padding-left: 1rem;
    padding-right: 1rem;
    margin: auto;
}

.v-item-group {
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}

.intro-action-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 4.5rem;
}

.backdrop {
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    bottom: 0px;
    background: rgb(0, 0, 0, 0.4);
    z-index: 950;
}
</style>