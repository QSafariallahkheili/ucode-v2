export interface PlanningIdeasState {
    
    planningIdeasFeatures: JSON;
  }
const planningIdeas = {
    namespaced: true,
    state: {
        planningIdeasFeatures: {}
    },
    mutations: {
        addPlanningIdeaFeatures(state: PlanningIdeasState, payload: JSON){
            state.planningIdeasFeatures = payload
        }
    },
    actions: {},
    getters: {},
};
  
export default planningIdeas;
  