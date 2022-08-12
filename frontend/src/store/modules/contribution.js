
import maplibregl from 'maplibre-gl'
import CommentPopupContent from '@/components/CommentPopupContent.vue'
import {createApp} from 'vue';
import { createVuetify } from 'vuetify'
import store from '../store.js'

const conntribution = {
    namespaced: true,
    state: {
        commentToggle: false,
        commentText: '',
        commentPosition: [],
        commentPopup: null,
        commentGeojson: {
            "type": "FeatureCollection",
            "features": []
        }
    },
    mutations:{
        setCommentToggle(state){
            state.commentToggle=!state.commentToggle
        }
    },
    actions:{
        createComment({state, rootState}){
            rootState.map.map.getCanvas().style.cursor = 'crosshair'
            rootState.map.map.once('click', (e) => {
                rootState.map.map.getCanvas().style.cursor = ''  
                if (state.commentToggle === true){
                    state.commentPosition= [e.lngLat.lng, e.lngLat.lat]

                    state.commentPopup = new maplibregl.Popup()
                    .setLngLat([e.lngLat.lng, e.lngLat.lat])
                    .setHTML('<div id="vue-popup-content"></div>')
                    .addTo(rootState.map.map)

                    const app = createApp(CommentPopupContent)
                    const vuetify = createVuetify()
                    app.use(vuetify)
                    app.use(store)
                    app.mount('#vue-popup-content')
                    state.commentToggle = false
                    
                }
            })            
        }

    },
    getters:{

    }

}

export default conntribution