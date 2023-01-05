<template>
    <v-bottom-navigation grow mode="shift" :elevation="6" color="secondary" :model-value="tabIndex" @update:modelValue="handleValueChange">
        <v-btn value="planning" >
            <v-icon v-if="projectType == 'transportation_planning'">mdi-road-variant</v-icon>
            <v-icon v-else-if="projectType == 'city_planning'">mdi-city-variant</v-icon>
            <v-icon v-else>mdi-message-draw</v-icon>
            
            <span>Planung</span>
        </v-btn>
        <v-btn value="discussion">
            <v-icon>mdi-comment-text-multiple</v-icon>
            <span>Diskussion</span> 
        </v-btn>
    </v-bottom-navigation>
    
</template>

<script setup>
    import { onMounted, ref } from "vue";
    import { useStore } from "vuex";

    const store = useStore()

    let projectType = ref (null)

    const props = defineProps({
        tabIndex: {
            type: String,
            default: "planning"
        }
    })

    const emit = defineEmits(['tabIndexChanged'])

    const handleValueChange = newValue => {
        if (newValue !== undefined){
            emit('tabIndexChanged', newValue)
        }
    }

    onMounted(() => {
        projectType.value = store.state.aoi.projectSpecification.project_type
    })
</script>

<style scoped>
    .v-bottom-navigation{
        position: absolute !important;
    }
    .v-btn{
        color: #747474;
    }
</style>