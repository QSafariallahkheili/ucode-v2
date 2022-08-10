<template>
<v-col
    cols="10"
    sm="1"
    style= "position: absolute; right: 0; top: 60px;z-index:999"
>
    <v-select
        :items="['get', 'retrieve']"
        label="building"
        variant="outlined"
        @update:modelValue="sendBuildingRequest"
    ></v-select>
   
   
</v-col>


</template>

<script setup>

const sendBuildingRequest = (e)=>{
    console.log(e)
}
</script>

<style scoped>

</style>