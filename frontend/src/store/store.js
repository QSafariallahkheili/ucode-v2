import { createStore } from "vuex";
import map from './modules/map';
import aoi from './modules/aoi';
import contribution from './modules/contribution';



export default createStore({
    modules: {
      map,
      aoi,
      contribution
    }
})