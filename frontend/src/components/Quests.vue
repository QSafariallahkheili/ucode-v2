<template >
  <div v-if="store.state.quests.hasQuests" class="quest-container">
    <v-window v-model="store.state.quests.current_order_id" :class="props.hide ? 'hide-window' : 'show-window'"
      class="quest-window">
      <v-window-item v-for="quest in store.state.quests.questList" :key="quest.order_id">
        <QuestCard :title="(quest.content?.title)" :description="(quest.content?.description)"
          :fulfillment="quest.fulfillment" :goal="quest.goal"
          @allQuestsCompleted="() => { showAllQuestsCompletedDialog = true; }" />
      </v-window-item>
    </v-window>
    <div>
      <div class="quest-action-area">
        <v-btn @click="hideBtnClicked">
          <v-icon icon="mdi-chevron-up" size="large"
            :class="props.hide ? 'rotate hide-btn-icon' : 'hide-btn-icon'"></v-icon>
        </v-btn>
      </div>
      <div>
        <transition name="fade">
          <QuestStepper v-if="!props.hide" :quests="store.state.quests.questList" />
        </transition>
      </div>

    </div>
    <QuestsCompletedDialog :show="showAllQuestsCompletedDialog"
      @allQuestsCompletedWasShown="() => { showAllQuestsCompletedDialog = false; }" />
  </div>
</template>

<script setup>
import { useStore } from "vuex";
import { prepareQuestsUserTable, getQuestsFulfillmentFromDB } from "@/service/backend.service";
import QuestCard from "@/components/QuestCard.vue";
import QuestStepper from "@/components/QuestStepper.vue"
import QuestsCompletedDialog from "@/components/QuestsCompletedDialog.vue"
import { watch, onMounted, ref, computed } from "vue"

const store = useStore();

const props = defineProps({
  hide: {
    type: Boolean,
    default: true
  }
})
const showAllQuestsCompletedDialog = ref(false)
const emit = defineEmits(["hideQuests"])

watch(store.state.quests, function (state) {
  if (Object.keys(state.questList).length === 0) {}
  else {
    store.state.quests.hasQuests = true;
    let quest = state.questList
    for (let i in state.questList) {
      if (quest[i]["order_id"] == state.current_order_id) {
        state.current_quest_type = quest[i].type
      }
    }
  }
})
await prepareQuestsUserTable(store.state.aoi.projectId, store.state.aoi.userId)

onMounted(() => {
  sendQuestRequest();
})

const sendQuestRequest = async () => {
  const questData = await getQuestsFulfillmentFromDB(store.state.aoi.projectId, store.state.aoi.userId)
  if (Object.keys(questData).length === 0) {
    console.log('No Quests in this Project! go crazy!')
    return
  }
  store.state.quests.questList = questData
  store.state.quests.current_order_id = questData[0].order_id
  // console.log(questData[0].quest_id)
}
const hideBtnClicked = () => {
  emit('hideQuests')
}

</script>

<style scoped>
.v-btn {
  margin-left: 1rem;
  margin-top: -0.5rem;
  height: 3rem;
  width: 3rem !important;
  min-width: 0px !important;
  padding: 0px !important;
  border-radius: 18px !important;
}

.quest-container {
  position: absolute;
  z-index: 1000;
  top: 0rem;
  left: 0rem;
  right: 0rem;
  margin-top: 0rem;
}

.quest-window {
  margin-top: 0rem;
  transition: margin-top 0.3s ease-in-out;
}

.hide-window {
  margin-top: -12rem !important;
}

.hide-btn-icon {
  transition: transform 0.4s ease-in-out;
}

.rotate {
  transform: rotate(180deg);
}

.quest-action-area {
  display: flex;
  position: absolute;

}

.quest-action-area>* {
  flex: 1 1 1;
}

.fade-enter-active {
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}

.fade-enter-to {
  opacity: 1;
}

.fade-leave-active {
  opacity: 1;
  transition: opacity 0.2s ease-in-out;
}

.fade-leave-to {
  opacity: 0;
}
</style>