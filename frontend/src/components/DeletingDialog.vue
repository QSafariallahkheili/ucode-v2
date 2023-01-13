<template>

<v-row justify="center">
    <v-dialog
      v-model="props.deleteDialog"
      persistent
     
    >
      <template v-slot:activator="{ props }">
        <v-btn
          color="primary"
          v-bind="props"
        >
          Open Dialog
        </v-btn>
      </template>
     
      <v-card>
        <span class="text-h6" >
          Are you sure you want to delete the comment?
        </span>
        <v-card-actions style="">
          <v-spacer></v-spacer>
          <v-btn
            color="green-darken-1"
            variant="text"
            @click="cnacelDeleteDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            color="red-darken-1"
            variant="text"
            @click="confirmDeleteCommentDialog"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>
<script setup lang="ts">
import {ref, toRefs } from 'vue';

const props = defineProps({
    deleteDialog: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(["cnacelDeleteDialog", "confirmDeleteCommentDialog"]);

const cnacelDeleteDialog = ()=>{
    emit("cnacelDeleteDialog")

}
const confirmDeleteCommentDialog = ()=>{
    emit("confirmDeleteCommentDialog")

}

</script>

<style scoped>

.v-dialog .v-overlay__content > .v-card, .v-dialog .v-overlay__content > .v-sheet {
  padding: 1rem;
    margin: 1.5rem 0rem;
    margin-left: 50%;
    transform: translateX(-50%);
    width: calc(100% - 3rem) !important;
    border-radius: 18px;
    border-radius: 18px;
}
</style>