<template>
  <div>


    <v-card
        theme="light"
        flat
        rounded="5"
        class="intro"
        style="border-radius: 18px 18px 0px 0px"

        
    >
        <v-window v-model="onboarding">
        <v-window-item
            v-for="n in sectionsLength"
            :key="`card-${n}`"
            :value="n"
        >
       
           
            <v-card-actions class="justify-space-between" style="padding: 0px !important;">
                <v-btn
                    variant="plain"
                    icon="mdi-chevron-left"
                    @click="prev"
                    :disabled="onboarding !=1 ? false : true"
                ></v-btn>
                <div class="text-body-1 font-weight-bold"> {{Object.keys(sections)[n-1]}} </div>
                <v-btn
                    variant="plain"
                    icon="mdi-chevron-right"
                    @click="next"
                    :disabled="onboarding !=sectionsLength ? false : true"
                ></v-btn>
            </v-card-actions>
            <div class="text-body-2 intro-text">{{Object.values(sections)[n-1]}}</div>
        </v-window-item>
        </v-window> 
        <v-card-actions class="justify-space-between">
        <v-item-group
            v-model="onboarding"
            class="text-center"
            mandatory
        >
            <v-item
            v-for="n in sectionsLength"
            :key="`btn-${n}`"
            v-slot="{ isSelected, toggle }"
            :value="n"
            >
            <v-btn
                icon="mdi-record"
                size="small"
                @click="toggle"
                :color="isSelected ? 'black' : 'grey'"
            ></v-btn>
            </v-item>
        </v-item-group>
        </v-card-actions>
        <div class="intro-action-area" v-if="onboarding ==3">
            <v-btn
                color="#5872FF"
                @click="closeIntro"
                class="final-btn"
            >
                Let's go
            </v-btn>
        </div>
        <div class="intro-action-area" v-if="onboarding !=3">
            <v-btn
                color="#5872FF"
                variant="plain"
                @click="next"
            >
                next
            </v-btn>
            <v-btn
                color="grey"
                variant="plain"
                class="justify-center align-center"
                @click="closeIntro"
                v-show="onboarding !=sectionsLength ? true : false"
                
            >
                I already know that
            </v-btn>
        </div>
       
    </v-card>
      
     <div class="backdrop"></div>
     </div>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { onMounted, reactive, ref } from "vue";
const store = useStore(); 

let onboarding = ref(0)
let sections = reactive ({
    'Project Goal': store.state.aoi.projectSpecification.project_goal,
    'How to Use This App': "Lorem ipsum dolor sit amet consectetur, adipisicing elit. Inventore suscipit harum deleniti doloremque vitae porro culpa, ea quaerat reiciendis voluptas repellat ad non, praesentium tenetur officiis eos repreLorem ipsum dolor sit amet consectetur, adipisicing elit. Inventore suscipit harum deleniti doloremque vitae porro culpa, ea quaerat reiciendis voluptas repellat ad non, praesentium tenetur officiis eos reprehenderit, ex iusto?henderit, ex iusto?",
    'Why Quests': "Lorem ipsum dolor sit amet consectetur, adipisicing elit. Inventore suscipit harum deleniti doloremque vitae porro culpa, ea quaerat reiciendis voluptas repellat ad non, praesentium tenetur officiis eos reprehenderit, ex iusto?",

})
let sectionsLength = ref(Object.keys(sections).length)

const next = () => {
    onboarding.value = onboarding.value + 1 > sectionsLength.value
        ? 1
        : onboarding.value + 1
}
const prev = () => {
    onboarding.value = onboarding.value - 1 <= 0
        ? sectionsLength.value
        :  onboarding.value - 1
}
const closeIntro = ()=>{
    store.state.ui.intro=false
}
</script>

<style scoped>

.intro {
  z-index: 1000;
  width: 100%;
  
  /* margin: auto;
  top: 30vh; */
}
.section-description{
    overflow: auto
}

.final-btn{
    color: white;
}

.v-card{
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 1.5rem;
}

.intro-text{
    margin-top: 0.5rem;
    min-height: 10rem;
    max-height: 10rem;
    overflow-y: scroll;
    padding-left: 1rem;
    padding-right: 1rem;
}

.v-item-group{
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}

.intro-action-area{
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 4.5rem;
}
.backdrop{
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    bottom: 0px;
    background: rgb(0,0,0,0.4);
    z-index: 950;
}
</style>