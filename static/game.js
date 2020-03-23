var Card = Vue.component('card', {
    props: {
        card: Object
    },
    methods: {
        card_input: function(event) {
          this.$root.card_input(this.card.onclickjson)
        }
    },
    template: '<button v-if="card.clickable" v-on:click="card_input">{{ card.value }}</button> \
               <div style="display: inline-block;"v-else>{{card.value}}</div>'
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
    template: '<div ><switchable v-for="ob in this.$root.objects[container.id].objects" :switchable="$root.objects[ob]"></switchable></div>'
})

Vue.component('game', {
    data: function () {
      return {
        games: gameConfig.game_id,
        curplayer: gameConfig.player,
        turn: 0,
        structure: {
            id: 0}
      };
    },
    methods: {
        new_game: function(event) {
          this.$root.new_game(this.games)
        },
        load_game: function(event) {
          this.$root.load_game(this.games)
        }
    },
    template: '<div><container :container="structure"></container><button v-on:click="load_game">Load Game</button></div> \
    <div><container :container="structure"></container><button v-on:click="new_game">New Game</button></div>'
  })

new Vue({
  el: '#components-demo',
  data: {
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
  methods: {
      new_game: function(games) {
        this.$children[0].games++;
        var game=this;
        console.log(this.$children[0]);
        axios.get('/game/start?groupid=1&type=tictactoe&gameid='+this.$children[0].games).then(
            function (response) {for (var objid in response.data.updates){
              game.$children[0].turn=response.data.turn;
              game.objects[objid] = response.data.updates[objid];
            }});
      },
      load_game: function(games) {
        var game=this;
        console.log(this.$children[0]);
        axios.get('/game/move?move=0&gameid='+this.$children[0].games).then(
            function (response) {for (var objid in response.data.updates){
              game.$children[0].turn=response.data.turn;
              game.objects[objid] = response.data.updates[objid];
            }});
      },
      card_input: function(card_json) {
          var game=this;
          console.log(game)
          var prop_data="";

          for (const property in card_json) {
            console.log(`${property}: ${card_json[property]}`);
            prop_data=prop_data+`&${property}=${card_json[property]}`;
          }
          axios.get('/game/move?gameid='+game.$children[0].games+'&move='+game.$children[0].turn+prop_data).then(
            function (response) {for (var objid in response.data.updates){
              game.$children[0].turn=response.data.turn;
              
              game.objects[objid] = response.data.updates[objid];
            }});
      },
      update_from_response: function(response_data) {
        game.$children[0].turn=response_data.turn;
        for (var objid in response_data.updates){
          for (var charid in response_data.updates[objid]){
            game.objects[objid][charid] = response.data.updates[objid][charid]
          }
        }
      }
  }
})




