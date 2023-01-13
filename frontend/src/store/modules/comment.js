import { HTTP } from '../../utils/http-common';

const comment = {
    namespaced: true,
    state: {
        toggle: false,
        commentData: {},
        likedCommentIds: [],
        unlikedCommentIds: [],
        deletedComments: []
    },
    mutations: {
        setCommentToggle(state) {
            state.toggle = true
        },
        getClickedCommentObject(state, payload) {
               // TH 19.10.2022 -> Time-relative Timestamd: 
            // when older than 1 week = the exact timestamp, 
            // when less than 24 houers = e.g. 9 hours before
            // when less tahn 1 hour before = 15 minutes before
            // >> I8n? -> translation for time strings: vor x Stunde, Stunden, Tag, Tagen, Monat, Monaten, Jahr, Jahren
            // not implemented yet
            /*
            
            - get current time
            - get stored time
            - make difference
            - if difference -> "created before" string

            */

            let date = new Date(payload.properties.created_at);
            let puretimestamp = date.toString()
            
            // TH 2022-11-07: if the timestamp is already modified, skip the modifikation
            if (puretimestamp.includes("GMT"))  {
                date = new Date(Date.parse(date));
                date = date.toUTCString();
                let day = new Date(date).getDate();
                let month = new Date(date).getMonth() + 1;
                let year = new Date(date).getFullYear();
                let hours = new Date(date).getHours();
                if (hours < 10) {
                    hours = "0" + hours
                };
    
                let minutes = new Date(date).getMinutes();
                if (minutes < 10) {
                    minutes = "0" + minutes
                };
    
                let seconds = new Date(date).getSeconds();
                if (seconds < 10) {
                    seconds = "0" + seconds
                };
                let newdate = day + "." +
                    month + "." +
                    year + "  " +
                    hours + ":" +
                    minutes + ":" +
                    seconds;
    
                payload.properties.created_at = newdate;    
    
            };
            
            state.commentData = payload 

        }
    },
    actions: {
        likeComment({ state, rootState }, payload) {
            if (state.likedCommentIds.includes(payload)) {
                state.commentData.properties.likes--
                const index = state.likedCommentIds.indexOf(payload);
                if (index > -1) {
                    state.likedCommentIds.splice(index, 1);
                }
                HTTP
                    .post('unlike-comment', {
                        id: payload,
                        projectId: rootState.aoi.projectSpecification.project_id
                    })

            }
            else {
                state.commentData.properties.likes++
                state.likedCommentIds.push(payload)
                HTTP
                    .post('like-comment', {
                        id: payload,
                        projectId: rootState.aoi.projectSpecification.project_id
                    })
            }

        },
        dislikeComment({ state, rootState }, payload) {
            if (state.unlikedCommentIds.includes(payload)) {
                state.commentData.properties.dislikes--
                const index = state.unlikedCommentIds.indexOf(payload);
                if (index > -1) {
                    state.unlikedCommentIds.splice(index, 1);
                }
                HTTP
                    .post('undislike-comment', {
                        id: payload,
                        projectId: rootState.aoi.projectSpecification.project_id
                    })

            }
            else {
                state.commentData.properties.dislikes++
                state.unlikedCommentIds.push(payload)
                HTTP
                    .post('dislike-comment', {
                        id: payload,
                        projectId: rootState.aoi.projectSpecification.project_id
                    })
            }
        }
    },
    getters: {

    }
}

export default comment