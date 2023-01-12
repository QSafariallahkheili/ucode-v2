import maplibregl from "maplibre-gl"

export interface freecommentState{
    moveComment: Boolean
}
const freecomment = {
    namespaced: true,
    state: {
        moveableCommentMarker: new maplibregl.Marker({draggable: true, color: '#0089B5', scale: 1.5})

        
    },
    mutations: {
       
    },
    actions: {
       
    },
    getters: {

    }
}

export default freecomment