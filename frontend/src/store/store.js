import { createStore } from "vuex";
import map from './modules/map';
import aoi from './modules/aoi';


export default createStore({
    modules: {
      map,
      aoi
    }
})