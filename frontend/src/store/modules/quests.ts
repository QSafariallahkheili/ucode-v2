export interface questsState {
    
  current_order_id: number;
  questList: JSON;
  selectedRouteId: boolean;
  current_quest_type: number
}

const quests = {
  namespaced: true,
  state: {
    current_order_id: 0,
    questList: {},
    selectedRouteId: null,
    current_quest_type: 0
  },
  mutations: {},
  actions: {},
  getters: {}
};

export default quests;
