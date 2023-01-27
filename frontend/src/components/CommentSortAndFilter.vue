<template>
   <div>
      <v-sheet class="mx-auto sorting-filtering-options" max-width="100%">
      
         <v-btn variant="text" icon="mdi-filter-variant" @click="toggleMultiCritFilterDialog"></v-btn>
         <v-select label="Sortieren nach"
            :items="['beliebte zuerst', 'unbeliebte zuerst', 'neuste zuerst', 'älteste zuerst', 'längste zuerst', 'kürzeste zuerst']"
            variant="solo" class="sort-select" density="compact" flat @update:modelValue="sortComment">
         </v-select>
         <div v-for="filterOption, index in props.activfilterOptions" :key="index">
            <v-btn height="40px" width="110px" size="medium" :class="filterOption.isActive?' filter-btn-is-active ml-2':'ml-2'" rounded="lg" :value="filterOption"
                flat
               @click="updateCommentFilters(filterOption)">
               <v-icon v-if="filterOption.isActive">
                  mdi-check
               </v-icon>
               <div v-if="filterOption.filterOptions.filterType == 'meine'">
                  meine
               </div>
               <div v-if="filterOption.filterOptions.filterType == 'quest'">
                  quest {{ filterOption.filterOptions.filterValue }}
               </div>
               <div v-if="filterOption.filterOptions.filterType == 'planningIdea'">
                  <v-icon
                     :color="store.state.planningIdeas.planningIdeasFeatures.features.filter((f: any) => f.properties.id == filterOption.filterOptions.filterValue)[0].properties?.color">
                     mdi-checkbox-blank-circle
                  </v-icon>
                  route {{ filterOption.filterOptions.filterValue }}
               </div>
               <div v-if="filterOption.filterOptions.filterType == 'keyword'">
                  {{ filterOption.filterOptions.filterValue }}
               </div>
            </v-btn>
         </div>
         <!-- <v-btn-toggle v-model="toggle" divided>
               <v-btn height="32px" size="small" class="ml-2" flat rounded="lg" value="meine"
                  @click="filterComment({ filterType: 'meine', filterValue: store.state.aoi.userId })">
                  Meine
               </v-btn>
               <div v-for="route in store.state.planningIdeas.planningIdeasFeatures.features"
                  :key="route.properties.id">

                  <v-btn height="32px" size="small" class="ml-2" rounded="lg" :value="route.properties.id" flat
                     @click="filterComment({ filterType: 'planningIdeas', filterValue: route.properties.id })">
                     <v-icon :color="route.properties.color">
                        mdi-checkbox-blank-circle
                     </v-icon>
                     <div>
                        route {{ route.properties.id }}
                     </div>
                  </v-btn>
               </div>
            </v-btn-toggle> -->

      </v-sheet>
      <CommentMultiCritFilter @multifilterComment="multifilterComment" @toggleWindow="toggleMultiCritFilterDialog"
         v-if="showMultiCritFilter" :activfilterOptions="props.activfilterOptions"/>
   </div>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { reactive, ref } from "vue"
import CommentMultiCritFilter from "@/components/CommentMultiCritFilter.vue"
const showMultiCritFilter = ref(false)

const store = useStore();
const props = defineProps({
   bottomPositionSortFilter: {
      type: String,
      default: ""
   },
   activfilterOptions:{
      type: Array<{ isActive: boolean, filterOptions: { filterType: string, filterValue: number|string }}>,
      default: []
   }
})
const emit = defineEmits(["sortComment", "multifFilterComment"])

const sortComment = (sortOption: string) => {
   emit("sortComment", sortOption)
}

const multifilterComment = (filterOption: { isActive: boolean, filterOptions: { filterType: string, filterValue: number|string  } }[]) => {
   emit("multifFilterComment", filterOption)
}
const updateCommentFilters = (filterOption: { isActive: boolean, filterOptions: { filterType: string, filterValue: number|string  } }) => {
   const changedFilter = props.activfilterOptions[props.activfilterOptions.indexOf(filterOption)]
   changedFilter.isActive = !changedFilter.isActive
   emit("multifFilterComment", props.activfilterOptions)
}

const toggleMultiCritFilterDialog = () => {
   showMultiCritFilter.value = !showMultiCritFilter.value
}

</script>

<style scoped>
.filter-btn-is-active{
   color: #0089B5;
   background: #EDF0FF;
}
.sorting-filtering-options::-webkit-scrollbar {
    display: none;
}
.sorting-filtering-options {
   background: rgba(255, 255, 255, 0.4);
   backdrop-filter: blur(5px);
   -webkit-backdrop-filter: blur(5px);
   -moz-backdrop-filter: blur(5px);
   -ms-backdrop-filter: blur(5px);
   padding: .3rem .5rem .3rem .5rem !important;
   position: fixed;
   z-index: 1000;
   width: 100%;
   bottom: v-bind(bottomPositionSortFilter);
   overflow-x: scroll;
   overflow-y: clip;
   scrollbar-width: none !important;
   display: flex;
   flex-direction: row;
   align-items: center;
   justify-content: flex-start;
}
.v-select__selections {
     min-height: 30px !important
}
.sort-select {
   max-width: 200px;
   min-width: 150px;
   height:40px;
   overflow-x: auto;
   overflow-y: clip;
}
.v-input__details{
   height:0px
}
.v-select__selection-text{
   overflow-x: hidden !important;
}
.v-btn{
    min-width: fit-content
}
</style>