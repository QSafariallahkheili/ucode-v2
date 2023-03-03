export interface questsState {
  current_order_id: number;
  questList: JSON;
  selectedRouteId: boolean;
  current_quest_type: number;
  hasQuests: boolean;
}
export interface Quest{
  quest_id: number;
  content: QuestContent;
  fulfillment: number;
  order_id: number;
  type: number;
  goal: number;
}
interface QuestContent{
  title: string;
  description: string;
  detailedDescription: string;
}


const quests = {
  namespaced: true,
  state: {
    current_order_id: 0,
    questList: {},
    selectedRouteId: null,
    current_quest_type: 0,
    hasQuests: false
  },
  mutations: {},
  actions: {},
  getters: {}
};

export default quests;
