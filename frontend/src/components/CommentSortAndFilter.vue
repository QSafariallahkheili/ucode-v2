<template>

   <v-sheet class="mx-auto sorting-filtering-options" max-width="100%">
      <v-slide-group show-arrows v-slot="{ isSelected }">
         <v-slide-group-item>
            <v-btn variant="text" icon=" mdi-filter-variant" :color="isSelected ? 'primary' : undefined"></v-btn>
            <v-select label="Sortieren nach"
               :items="['beliebte zuerst', 'unbeliebte zuerst', 'neuste zuerst', 'älteste zuerst', 'längste zuerst', 'kürzeste zuerst']"
               variant="solo" class="sort-select" density="compact" @update:modelValue="sortComment">
            </v-select>
         </v-slide-group-item>
      </v-slide-group>

   </v-sheet>
</template>

<script lang="ts" setup>
const emit = defineEmits(["sortComment"])
const sortComment = (sortOption: string) => {
   emit("sortComment", sortOption)

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

}

.sort-select {
   max-width: 200px;
   min-width: 150px;
   vertical-align: middle;

}
</style>