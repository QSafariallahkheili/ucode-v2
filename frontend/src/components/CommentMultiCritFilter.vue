<template>
    <div class="filter-container">
        <v-card v-click-outside="closeWindow" style="border-radius: 18px 18px 0px 0px">
            <v-btn @click="closeWindow"  icon="mdi-close" class="close-button"  variant="plain">
            </v-btn>
            <div class="filter-headline text-h6 font-weight-bold text-center"> Filter </div>
            <div class="filter-content">
                <v-btn-toggle v-model="filterMeine">
                    <v-btn height="32px" width="90px" size="small"
                        :class="filterMeine? 'ma-1 filter-btn-is-active' : 'ma-1'"
                        variant="tonal" rounded="lg" :value="{ filterType: 'meine', filterValue: '' }">
                        Meine
                    </v-btn>
                </v-btn-toggle>
                <div class="filter-sub-headline text-subtitle-1 font-weight-bold"> Planungsvarianten </div>
                <v-btn-toggle v-model="filterPlanningIdeas" multiple>
                    <div v-for="route in store.state.planningIdeas.planningIdeasFeatures.features"
                        :key="route.properties.id">
                        <v-btn height="32px" width="90px" size="small"
                            :class="filterPlanningIdeas?.map((filter) => filter.filterValue).includes(route.properties.id) ? 'ma-1 filter-btn-is-active' : 'ma-1'"
                            variant="tonal" rounded="lg"
                            :value="{ filterType: 'planningIdea', filterValue: route.properties.id }">
                            <v-icon :color="route.properties.color">
                                mdi-checkbox-blank-circle
                            </v-icon>
                            route {{ route.properties.id }}
                        </v-btn>
                    </div>
                </v-btn-toggle>
                <div class="filter-sub-headline text-subtitle-1 font-weight-bold"> Quests </div>
                <v-btn-toggle v-model="filterQuests" multiple>
                    <div v-for="quest in store.state.quests.questList" :key="quest.order_id">
                        <v-btn height="32px" width="90px" size="small"
                            :class="filterQuests?.map((filter) => filter.filterValue).includes(quest.quest_id) ? 'ma-1 filter-btn-is-active' : 'ma-1'"
                            variant="tonal" rounded="lg" :value="{ filterType: 'quest', filterValue: quest.quest_id }"
                            tonal>
                            quest {{ quest.order_id + 1 }}
                        </v-btn>
                    </div>
                </v-btn-toggle>
                <div class="filter-sub-headline text-subtitle-1 font-weight-bold"> Schlüsselwörter </div>

                <v-text-field class="ml-2" variant="underlined" placeholder="Kommentare filtern nach..."
                    @keyup.native.enter="submitKeyword" v-model="keyword"></v-text-field>
                <v-btn-toggle v-model="filterKeywords" multiple>
                    <div v-for="keyword in keywords" :key="keyword">
                        <v-btn calss="keyword-btn" height="32px" width="90px" size="small"
                            :class="filterKeywords?.map((filter) => filter.filterValue).includes(keyword) ? 'ma-1 filter-btn-is-active' : 'ma-1'"
                            variant="tonal" rounded="lg" :value="{ filterType: 'keyword', filterValue: keyword }">
                            {{ keyword }}
                        </v-btn>
                    </div>
                </v-btn-toggle>
                <!-- <v-combobox v-model="filterKeywordsAr" chips label="Schlüsselwörter" multiple variant="solo">
                    <template v-slot:selection="{ attrs, item, select, selected }">
                        <v-chip v-bind="attrs" :model-value="selected" closable @click="select">
                            <strong>{{ item }}</strong>&nbsp;
                            <span>(interest)</span>
                        </v-chip>
                    </template>
                </v-combobox> -->
            </div>
            <v-btn color=secondary variant="text" @click="applyMultiCritFilter">
                Anwenden
            </v-btn>
        </v-card>
        <div class="backdrop"></div>
    </div>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { computed, onBeforeUpdate, onMounted, reactive, ref, watch } from "vue";
const store = useStore();
const keyword = ref<string>("")
const keywords: string[] = reactive([])
const filterMeine = ref<{ filterType: string, filterValue: number|string }>()
const filterPlanningIdeas = ref<{ filterType: string, filterValue: number|string }[]>([])
const filterQuests = ref<{ filterType: string, filterValue: number|string }[]>([])
const filterKeywords = ref<{ filterType: string, filterValue: number|string }[]>([])
const emit = defineEmits(["multifilterComment", "toggleWindow"])
const props = defineProps({
    show: {
        type: Boolean,
        default: false
    },
    shownQuickFilters: Array,
    activfilterOptions: {
        type: Array<{ isActive: boolean, filterOptions: { filterType: string, filterValue: number|string } }>,
        default: []
    }
})

const updateFilterSelection = () => {
    props.activfilterOptions.map(filter => {
        if (filter.filterOptions.filterType == 'meine') {
            if (filter.isActive) {
                filterMeine.value !== (filter.filterOptions) ? filterMeine.value = filter.filterOptions : filterMeine.value = undefined
            }
            else {
                filterMeine.value = undefined
            }
        }
        else if (filter.filterOptions.filterType == 'planningIdea') {
            if (filter.isActive) {
                !filterPlanningIdeas.value.includes(filter.filterOptions)? filterPlanningIdeas.value.push(filter.filterOptions): undefined
                    
            }
            else {
                filterPlanningIdeas.value.includes(filter.filterOptions) ? filterPlanningIdeas.value.splice(filterPlanningIdeas.value.indexOf(filter.filterOptions)) : undefined
            }
        }
        else if (filter.filterOptions.filterType == 'quest') {
            if (filter.isActive) {
                !filterQuests.value.includes(filter.filterOptions) ? filterQuests.value.push(filter.filterOptions) : undefined
            }
            else {
                filterQuests.value.includes(filter.filterOptions) ? filterQuests.value.splice(filterQuests.value.indexOf(filter.filterOptions)) : undefined
            }
        }
        else if (filter.filterOptions.filterType == 'keyword') {
            //@ts-ignore
            let value:string=filter.filterOptions.filterValue
            if (filter.isActive) {
                !filterKeywords.value.includes(filter.filterOptions) ? filterKeywords.value.push(filter.filterOptions) : undefined
                !keywords.includes(value)? keywords.push(value): undefined
            }
            else {
                filterKeywords.value.includes(filter.filterOptions) ? filterKeywords.value.splice(filterKeywords.value.indexOf(filter.filterOptions)) : undefined
                !keywords.includes(value)? keywords.push(value): undefined
            }

        }
    })

}
onMounted(()=>{
    updateFilterSelection();

})

// watch(props.activfilterOptions, function () {
//     console.log("update")
//     updateFilterSelection()
    
// })
const submitKeyword = () => {
    // console.log(keyword)
    if(keyword.value == ""){return}
    !keywords.includes(keyword.value)? keywords.push(keyword.value): undefined
    keyword.value = ""
}

const filterOptions = computed(() => {
    let fo = reactive<{ filterType: string, filterValue: number|string }[]>([])
    if (filterMeine.value) {
        fo.push(filterMeine.value)
    }
    if (filterPlanningIdeas) {
        filterPlanningIdeas.value.forEach((value) => {
            fo.push(value)
        })
    }
    if (filterQuests) {
        filterQuests.value.forEach((value) => {
            fo.push(value)
        })
    }
    if (filterKeywords) {
        filterKeywords.value.forEach((value) => {
            fo.push(value)
        })
    }
    let filter: { isActive: true, filterOptions: { filterType: string, filterValue: number|string } }[] = []
    fo.map(filterOption => filter.push({ isActive: true, filterOptions: filterOption }))
    return filter
})

const applyMultiCritFilter = () => {
    emit("multifilterComment", filterOptions.value)
    emit("toggleWindow")
}
const closeWindow=()=>{
    updateFilterSelection()
    emit('toggleWindow')
}
</script>

<style scoped>
.close-button{
    touch-action: none;
    position: relative; 
    margin: 0em 0em 0em auto;
}
.filter-btn-is-active {
    color: #0089B5;
    background: #EDF0FF;
}

.filter-container {
    z-index: 1102;
    width: 100%;
    margin-bottom: 0px;
    scrollbar-width: none !important;
    position: fixed;
    bottom: 56px;
}

.filter-headline {
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
}

.projectInfo-content::-webkit-scrollbar {
    display: none;
}

.filter-content {
    overflow-y: scroll;
}

.v-btn-toggle {
    display: flex;
    align-items: center !important;
    flex-wrap: wrap;
    height: auto

}

.v-card {
    z-index: 1102;
    display: flex;
    flex-direction: column;
    align-items: center;
    max-height: 100vh;

}


.filter-sub-headline {
    margin-top: 0.5rem;
    max-width: 35rem;
    padding-left: 1rem;
    padding-right: 1rem;
    color: gray
}

.info-text {
    margin-top: 0.5rem;
    max-height: 100%;
    max-width: 35rem;
    overflow-y: scroll;
    padding-left: 1rem;
    padding-right: 1rem;
    margin: auto;
}

.v-item-group {
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    overflow-y: scroll;
}

.backdrop {
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    bottom: 0px;
    background: rgb(0, 0, 0, 0.8);
    z-index: 1101;
}
.keyword-btn{
    min-width: fit-content
}

</style>