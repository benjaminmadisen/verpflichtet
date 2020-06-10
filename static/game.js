var Card = Vue.component('card', {
    props: {
        card: Object
    },
    methods: {
        card_input: function(event) {
          this.$root.card_input(this.card.onclickjson)
        }
    },
    template: '<button v-if="card.clickable" v-on:click="card_input" v-bind:style="[\'style\' in card ? card.style : {display: \'inline-block\'}]" >{{ card.value }}</button> \
               <div v-else v-bind:style="[\'style\' in card ? card.style : {display: \'inline-block\'}]">{{card.value}}</div>'
  })

var Switchable = Vue.component('switchable', {
    props: {
        switchable: Object
    },
    template: '<container v-if="switchable.type == `container`" :container="switchable"></container>\
               <card v-else :card="switchable"></card>'
})

var Container = Vue.component('container', {
    props: {
        container: Object
    },
    template: '<div v-bind:style="[\'style\' in container ? container.style : {}]"><switchable v-for="ob in this.$root.objects[container.id].objects" :switchable="$root.objects[ob]"></switchable></div>'
})

Vue.component('game', {
    data: function () {
      return {
        games: gameConfig.game_id,
        curplayer: gameConfig.player_id,
        turn: 0,
        structure: {
            id: 0}
      };
    },
    methods: {
    },
    template: '<div><container :container="structure"></container></div>'
  })
var socket = io('http://localhost:5000');
Vue.use(VueSocketIOExt, socket);
console.log("here");
new Vue({
  el: '#components-demo',

  data: {
    update: true,
    objects: {0:{
      id: 0,
      type: 'container',
      objects: [1]},
      1:{
        id: 1,
        type: 'card',
        clickable: false,
        value: "hi"}
    }
  },
  mounted: function() {
    this.$socket.client.emit('join',{'game_id':gameConfig.game_id});
  },
  methods: {
      card_input: function(card_json) {
          var game=this;
          /*
          console.log(game)
          var prop_data="";

          for (const property in card_json) {
            console.log(`${property}: ${card_json[property]}`);
            prop_data=prop_data+`&${property}=${card_json[property]}`;
          }
          */
          this.$socket.client.emit('move',{'game_id':game.$children[0].games,'move':game.$children[0].turn,'data':card_json});
          /*
          axios.get('/game/move?gameid='+game.$children[0].games+'&move='+game.$children[0].turn+prop_data).then(
            update_from_response(response.data));
            */
      },
      update_from_response: function(response_data) {
        console.log("got response");
        console.log(response_data);
        var game=this;
        //game.$children[0].turn=response_data.turn;
        if ('turn' in response_data){
            game.$children[0].turn=response_data.turn;
        }
        for (var objid in response_data.updates){
          if (!(objid in game.objects)){
            Vue.set(game.objects,objid,{});
          }
          for (var charid in response_data.updates[objid]){
            //console.log(response_data.updates[objid][charid])
            if (charid!='style'){
                Vue.set(game.objects[objid],charid,response_data.updates[objid][charid]);
            }
            else{
                if(!('style' in game.objects[objid])){
                    Vue.set(game.objects[objid],charid,{});
                } 
                for (var styleid in response_data.updates[objid][charid]){
                    Vue.set(game.objects[objid][charid],styleid,response_data.updates[objid][charid][styleid]);
                }
                
                console.log(response_data.updates[objid][charid])
            }
          }
        }
      }
  },
    sockets: {
      connect: function () {
        console.log('socket connected');
        },
      update: function (data) {
        console.log(data)
        this.update_from_response(data);
      },
      disconnect: function() {
        console.log('connect closed');
    }
  }
})




