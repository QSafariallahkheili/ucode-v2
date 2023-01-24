<template>

   <v-sheet class="mx-auto sorting-filtering-options" max-width="100%">
      <v-slide-group show-arrows v-slot="{ isSelected }">
         <v-slide-group-item>
            <v-btn variant="text" icon=" mdi-filter-variant" :color="isSelected ? 'primary' : undefined"></v-btn>
            <v-select label="Sortieren nach"
               :items="['beliebte zuerst', 'unbeliebte zuerst', 'neuste zuerst', 'älteste zuerst', 'längste zuerst', 'kürzeste zuerst']"
               variant="solo" class="sort-select" density="compact" @update:modelValue="sortComment">
            </v-select>
            <v-btn-toggle v-model="toggle" divided>
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
                     route {{ route.properties.id }}
                  </v-btn>
               </div>
            </v-btn-toggle>

         </v-slide-group-item>
      </v-slide-group>

   </v-sheet>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { ref } from "vue"
const store = useStore();
const props = defineProps({
   bottomPositionSortFilter: {
      type: String,
      default: ""
   }
})

let toggle = ref(null)
const emit = defineEmits(["sortComment", "filterComment"])
const sortComment = (sortOption: string) => {
   emit("sortComment", sortOption)

}
const filterComment = (filterOption: { filterType: string, filterValue: string }) => {
   console.log(toggle.value)
   if (!toggle.value) {
      emit("filterComment", null)
   }
   else {
      emit("filterComment", filterOption)
   }
}



</script>

<style scoped>
.sorting-filtering-options {
   background: rgba(255, 255, 255, 0.4);
   backdrop-filter: blur(5px);
   -webkit-backdrop-filter: blur(5px);
   -moz-backdrop-filter: blur(5px);
   -ms-backdrop-filter: blur(5px);
   padding: .5rem 1.5rem .5rem 1.5rem !important;
   position: fixed;
   z-index: 1000;
   width: 100%;
   bottom: v-bind(bottomPositionSortFilter);
}

.sort-select {
   max-width: 200px;
   min-width: 150px;
   vertical-align: bottom;
   height: 0
}
</style>