import { createRouter, createWebHistory } from "vue-router";
import Map from "@/components/Map.vue";

const routes = [
    {
        path: "/",
        name: "home",
        component: Map,
    }
]

const router = createRouter({ history: createWebHistory(), routes })


export default router