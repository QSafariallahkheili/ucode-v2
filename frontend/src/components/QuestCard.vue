<template >
    <v-card elevation="5">
        <div class="text-body-1 font-weight-bold">{{ props.title }}</div>
        <div class="text-body-1">{{ props.description }}</div>
        <QuestProgressbar :fulfillment="props.fulfillment" :goal="props.goal"/>
    </v-card>
</template>

<script lang="ts" setup>
import QuestProgressbar from "@/components/QuestProgressbar.vue";
const props = defineProps({
    title: {
        type: String,
        default: "Title"
    },
    description: {
        type: String,
        default: "short description"
    },
    fulfillment: {
        type: Number,
        default: 0
    },
    goal: {
        type: Number,
        default: 3
    }
})
</script>

<style scoped>
.v-card{
    position: absolute;
    z-index: 1000;
    padding: 1.5rem;
    border-radius: 18px;
    top: 1rem;
    left: 1rem;
    right: 1rem;
}
</style>