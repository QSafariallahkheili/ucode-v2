<template>
    <div class="background">
        <v-btn
            v-for="quest in props.quests"
            :key="quest.order_id"
            variant="text"
            :icon="quest.fulfillment>=quest.goal?'mdi-checkbox-marked-circle':'mdi-record'"
            size="x-small"
            :color="store.state.quests.current_order_id===quest.order_id?'#ffffff':'rgb(0,0,0,0.4)'"
            @click="() => {store.state.quests.current_order_id = quest.order_id}"
        ></v-btn>
    </div>
</template>

<script setup>
import { useStore } from "vuex";

const store = useStore();

const props = defineProps({
    quests: {
        default: 1
    }
})
</script>

<style scoped>
.v-btn{
    transition: color 0.3s;
}
.background{
    display: flex;
    position:absolute;
    margin-left: 50%;
    transform: translateX(-50%);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    background: rgba(200,200,200,0.4);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    -moz-backdrop-filter: blur(5px);
    -ms-backdrop-filter: blur(5px);
}
</style>