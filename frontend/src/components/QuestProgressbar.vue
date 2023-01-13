<template>  
    <div class="bar-background" @click="onClick">
        <div class="bar-fulfillment" :style="{ marginLeft: getFulfillmentInPercent()-50+'%' }" ></div>
        <div
            class="step"
            v-for="n in props.goal-1"
            :key="n"
            :style="{ left: Math.round(n*100/props.goal) +'%' }"
        ></div>
    </div>
    <div :class="props.fulfillment>=props.goal?'text-caption font-weight-medium bar-label success-label':'text-caption bar-label text-medium-emphasis'">
        {{ props.fulfillment }} von {{ props.goal }}
    </div>
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
    fulfillmentInPercent.value = getFulfillmentInPercent()
    // console.log(fulfillmentInPercent.value)
})

const getFulfillmentInPercent = () => {
    return props.fulfillment>props.goal?100:Math.round(props.fulfillment*100/props.goal);
}
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
    background: #0089B5;
    height: 8px;
    width: 100%;
    margin-left: -50%;
    transform: translateX(-50%);
    transition: margin-left 0.3s ease-in-out;
    transition-delay: 0.3s;
}
.bar-label{
    width: fit-content !important;
    margin-top: 0.5rem;
    margin-left: 50%;
    transform: translateX(-50%);
    transition: color 0.1s;
}
.success-label{
    color: #0089B5 !important;
}

.step{
    position: absolute;
    top: 0;
    width: 2px;
    height: 100%;
    background: rgb(255,255,255,0.9);
    transform: translateX(-50%);
}
</style>