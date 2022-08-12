<template>
<div style="position:absolute; left: 20px; top:10px; z-index:999">
    <v-btn
        rounded="pill"
        color="secondary"
        @click="setCommentToggle(); createComment()"
    >
        Comment
    </v-btn>
</div>
   
</template>

<script setup>

import {useStore} from "vuex";
const store = useStore();


const setCommentToggle = ()=>{
    store.commit("contribution/setCommentToggle")
}

const createComment = ()=>{
    if (store.state.contribution.commentToggle == true){
        store.dispatch("contribution/createComment")
    }
}



</script>

<style scoped>

</style>