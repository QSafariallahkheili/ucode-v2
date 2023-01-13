<template >
    <v-card elevation="5">
        <div class="text-body-1 font-weight-bold">{{ props.title }}</div>
        <div class="text-body-1 quest-description">{{ props.description }}</div>
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
    margin: 1rem 1rem;
    padding: 1.5rem;
    border-radius: 18px;
}
.quest-description{
    min-height: 4.5rem;
    max-height: 4.5rem;
    font-size: 14px !important;
}
</style>