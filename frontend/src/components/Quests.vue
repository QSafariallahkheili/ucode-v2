<template >
  <QuestCard

    :title="(demoQuest.content?.title)"
    :description="(demoQuest.content?.description)"
    :fulfillment="demoQuest.fulfillment"
    :goal="demoQuest.goal"

  />
</template>

<script setup>
import { useStore } from "vuex";
import { prepareQuestsUserTable, getQuestsFulfillmentFromDB } from "@/service/backend.service";
import QuestCard from "@/components/QuestCard.vue";
import { onMounted, ref } from "vue";

const store = useStore();

let questList = ref([])
let demoQuest = ref({})

await prepareQuestsUserTable(store.state.aoi.projectId, store.state.aoi.userId)

onMounted(() => {
    sendQuestRequest();

})

const sendQuestRequest = async () => {
      const questData = getQuestsFulfillmentFromDB(store.state.aoi.projectId,store.state.aoi.userId)
      questList.value = (await questData).data

      //test
      console.log((await questData).data)
      demoQuest.value = (await questData).data[1]
}

</script>

<style scoped>
</style>