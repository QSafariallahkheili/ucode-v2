<template>
    <div class="filter-container">
        <div class="backdrop"></div>
        <v-card v-click-outside="closeWindow" style="border-radius: 18px 18px 0px 0px">
            <v-btn @click="closeWindow" icon="mdi-close" class="close-button" variant="plain">
            </v-btn>
            <div class="filter-headline text-h6 font-weight-bold text-center"> Filter </div>
            <div class="filter-content">
                <v-btn-toggle v-model="filterMeine">
                    <v-btn height="32px" width="90px" size="small"
                        :class="filterMeine ? 'ma-1 filter-btn-is-active' : 'ma-1'" variant="tonal" rounded="lg"
                        :value="{ filterType: 'meine', filterValue: '' }">
                        Meine
                    </v-btn>
                </v-btn-toggle>
                <div v-if="store.state.planningIdeas.planningIdeasFeatures.features"
                    class="filter-sub-headline text-subtitle-1 font-weight-bold"> Planungsvarianten </div>
                <v-btn-toggle v-model="filterPlanningIdeas" multiple>
                    <div v-for="route in store.state.planningIdeas.planningIdeasFeatures.features"
                        :key="route.properties.id">
                        <v-btn height="32px" min-width="90px" size="small"
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
                <div v-if="store.state.quests.questList[0]" class="filter-sub-headline text-subtitle-1 font-weight-bold">
                    Quests </div>
                <v-btn-toggle v-model="filterQuests" multiple>
                    <div v-for="quest in store.state.quests.questList.slice(1)" :key="quest.order_id">
                        <v-btn height="32px" min-width="90px" size="small"
                            :class="filterQuests?.map((filter) => filter.filterValue).includes(quest.order_id) ? 'ma-1 filter-btn-is-active' : 'ma-1'"
                            variant="tonal" rounded="lg" :value="{ filterType: 'quest', filterValue: quest.order_id}"
                            tonal>
                            quest {{ quest.order_id}}
                        </v-btn>
                    </div>
                </v-btn-toggle>
                <div class="filter-sub-headline text-subtitle-1 font-weight-bold"> Schlüsselwörter </div>

                <v-text-field class="ml-2" variant="underlined" placeholder="Kommentare filtern nach..."
                    @keyup.native.enter="submitKeyword" v-model="keyword"></v-text-field>
                <v-btn-toggle v-model="filterKeywords" multiple>
                    <div v-for="keyword, index in keywords" :key="keyword">
                        <v-btn ref="keyword-btn" class="keyword-btn" height="32px" size="small"
                            :class="filterKeywords?.map((filter) => filter.filterValue).includes(keyword) ? 'ma-1 pr-5 filter-btn-is-active' : 'pr-5 ma-1'"
                            variant="tonal" rounded="lg" :value="{ filterType: 'keyword', filterValue: keyword }">
                            {{ keyword }}
                            <v-icon class="delete-icon" small @click.stop="deleteKeyword(index)">mdi-close</v-icon>
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
    </div>
</template>

<script lang="ts" setup>
import { useStore } from "vuex";
import { computed, onMounted, reactive, ref, watch } from "vue";
const store = useStore();
const keyword = ref<string>("")
const keywords: string[] = reactive([])
interface FilterOption {
    filterType: string;
    filterValue: number | string;
}
interface ActiveFilter {
    isActive: boolean;
    filterOptions: FilterOption;
}
const filterMeine = ref<FilterOption>()
const filterPlanningIdeas = ref<FilterOption[]>([])
const filterQuests = ref<FilterOption[]>([])
const filterKeywords = ref<FilterOption[]>([])
const allFilterKeywords = ref<FilterOption[]>([])
const emit = defineEmits(["multifilterComment", "toggleWindow"])
const props = defineProps({
    show: {
        type: Boolean,
        default: false
    },
    shownQuickFilters: Array,
    activfilterOptions: {
        type: Array<{ isActive: boolean, filterOptions: { filterType: string, filterValue: number | string } }>,
        default: []
    }
})

watch(filterKeywords.value, (newValue) => {
    newValue.map(value => {
        if (!allFilterKeywords.value.includes(value)) {
            allFilterKeywords.value.push(value);
        }
    });
});
const deleteKeyword = (index: number) => {
    const keyword = keywords[index];
    keywords.splice(index, 1);
    filterKeywords.value = filterKeywords.value.filter(kw => kw.filterValue !== keyword);
    allFilterKeywords.value = allFilterKeywords.value.filter(akw => akw.filterValue !== keyword);
}
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
                !filterPlanningIdeas.value.includes(filter.filterOptions) ? filterPlanningIdeas.value.push(filter.filterOptions) : undefined

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
            let value: string = filter.filterOptions.filterValue
            if (filter.isActive) {
                !filterKeywords.value.includes(filter.filterOptions) ? filterKeywords.value.push(filter.filterOptions) : undefined
                !keywords.includes(value) ? keywords.push(value) : undefined
            }
            else {
                filterKeywords.value.includes(filter.filterOptions) ? filterKeywords.value.splice(filterKeywords.value.indexOf(filter.filterOptions)) : undefined
                !keywords.includes(value) ? keywords.push(value) : undefined
                allFilterKeywords.value.push({ filterType: 'keyword', filterValue: value })
            }

        }
    })

}
onMounted(() => {
    updateFilterSelection();

})

const submitKeyword = () => {
    // console.log(keyword)
    if (keyword.value == "") { return }
    !keywords.includes(keyword.value) ? keywords.push(keyword.value) : undefined
    filterKeywords.value.push({ filterType: 'keyword', filterValue: keyword.value })
    keyword.value = ""
}

const filterOptions = computed<ActiveFilter[]>(() => {
  const fo = filterMeine.value ? [filterMeine.value] : []  // Use ternary operator to create an array with filterMeine if it exists, otherwise an empty array
   return fo.concat(filterPlanningIdeas.value, filterQuests.value, filterKeywords.value)// Use concat to concatenate filterPlanningIdeas, filterQuests, and filterKeywords into a single array, then map over it
    .map(filterOption => ({// Map each filter option to an object with isActive set to true and filterOptions set to the option
      isActive: true, filterOptions: filterOption}))// Use concat to concatenate allFilterKeywords into the array, but only if the keyword isn't already in filterKeywords
    .concat(allFilterKeywords.value.filter(filterOption =>
      !filterKeywords.value.some(kw => kw.filterValue === filterOption.filterValue)
    ).map(filterOption => ({ isActive: false, filterOptions: filterOption })))
})

const applyMultiCritFilter = () => {
    //check if something is in the inputfield
    if (keyword.value.trim() !== '') {
        submitKeyword();
    }
    emit("multifilterComment", filterOptions.value)
    emit("toggleWindow")
}
const closeWindow = () => {
    applyMultiCritFilter()
}
</script>

<style scoped>
.close-button {
    touch-action: none;
    position: relative;
    margin: 0em 0em 0em auto;
}


.filter-btn-is-active {
    color: #0089B5;
    background: #EDF0FF;
}

.filter-container {
    z-index: 1002;
    width: 100%;
    margin-bottom: 0px;
    scrollbar-width: none !important;
    position: fixed;
    bottom: 56px;
}

.filter-headline {
    margin-bottom: 1.5rem;
}

.projectInfo-content::-webkit-scrollbar {
    display: none;
}

.filter-content {
    overflow-y: scroll;
    display: flex;
    flex-direction: column;
    min-width: 80%;

}

.v-btn-toggle {
    display: flex;
    align-items: center !important;
    flex-wrap: wrap;
    height: auto
}

.v-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    max-height: 100vh;
    min-height: 500px;
    padding: 1rem 1rem 1.5rem 1.5rem;
}


.filter-sub-headline {
    margin-top: 0.5rem;
    max-width: 35rem;
    padding-left: 1rem;
    padding-right: 1rem;
    color: gray
}

.backdrop {
    position: fixed;
    top: 0px;
    width: 100vw;
    height: 100%;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    -moz-backdrop-filter: blur(24px);
    -ms-backdrop-filter: blur(24px);
    background:#00000010;
}

.keyword-btn .v-btn {
    min-width: fit-content
}

.delete-icon {
    position: absolute;
    top: 2px;
    right: 2px;
}
</style>