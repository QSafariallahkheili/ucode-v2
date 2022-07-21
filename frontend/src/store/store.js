import { createStore } from "vuex";
import map from './modules/map';

export default createStore({
    modules: {
      map
    }
})