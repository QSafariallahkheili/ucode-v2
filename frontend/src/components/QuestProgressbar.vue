<template>  
    <div class="bar-background" @click="onClick">
        <div class="bar-fulfillment" :style="{ marginLeft: fulfillmentInPercent-50+'%' }" ></div>
    </div>
    <div class="text-caption bar-label" >{{ props.fulfillment }} von {{ props.goal }}</div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

const props = defineProps({
    fulfillment: {
        type: Number,
        default: 0
    },
    goal: {
        type: Number,
        default: 3
    }
})

let fulfillmentInPercent = ref(0);

onMounted(() => {
    fulfillmentInPercent.value = Math.round(props.fulfillment*100/props.goal)
    console.log(fulfillmentInPercent.value)
})
</script>

<style scoped>
.bar-background{
    background: #D9D9D9;
    border-radius: 8px;
    height: 8px;
    width: 90%;
    margin-top: 1rem;
    margin-left: 50%;
    transform: translateX(-50%);
    overflow: hidden;
}
.bar-fulfillment{
    background: #6D8B6B;
    height: 8px;
    width: 100%;
    margin-left: -50%;
    transform: translateX(-50%);
    transition: margin-left 0.3s ease-in-out;
}
.bar-label{
    width: fit-content !important;
    color: rgb(0,0,0,0.58) !important;
    margin-top: 0.5rem;
    margin-left: 50%;
    transform: translateX(-50%);
}
</style>