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
               <li v-else>{{card.value}}</li>'
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
    template: '<div><switchable v-for="ob in this.$root.objects[container.id].objects" :switchable="$root.objects[ob]"></switchable></div>'
})

Vue.component('game', {
    data: function () {
      return {
        games: 1,
        curplayer: 0,
        structure: {
            id: 0}
      };
    },
    methods: {
        new_game: function(event) {
          this.$root.new_game(this.games)
        }
    },
    template: '<div><container :container="structure"></container><button v-on:click="new_game">New Game</button></div>'
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
        axios.get('/game/start?groupid=1&type=tictactoe&gameid='+games).then(
            function (response) {for (var objid in response.data.updates){
              game.objects[objid] = [response.data.updates[objid]];
            }});
      },
      card_input: function(card_json) {
        var game=this;
          axios.get('/game/move?gameid='+this.$children[0].games+'&playerid='+this.$children[0].curplayer+'&move='+card_json).then(
            function (response) {for (var objid in response.data.updates){
              game.objects[objid] = [response.data.updates[objid]];
            };
            this.$children[0].curplayer++;
            if(this.$children[0].curplayer > 1){this.$children[0].curplayer = 0};})
      }
  }
})
