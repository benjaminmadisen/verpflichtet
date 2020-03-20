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
    template: '<div><switchable v-for="ob in container.objects" :switchable="ob"></switchable></div>'
})

Vue.component('game', {
    data: function () {
      return {
        games: 1,
        curplayer: 0,
        structure: {
            id: 0,
            type: 'container',
        objects: [{
            id: 1,
            type: 'card',
            value: "",
            clickable: true,
            visible: true,
            updateable: true,
            image: "",
            shape: "",
            position: "",
            onclickjson: ""
          },
          {
            id: 2,
            type: 'card',
            value: "",
            clickable: true,
            visible: true,
            updateable: true,
            image: "",
            shape: "",
            position: "",
            onclickjson: ""
          }]}
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
  methods: {
      new_game: function(games) {
        this.$refs[0].$refs.game.games++;
        axios.get('/game/start?groupid=1&type=tictactoe&gameid='+games).then(
            function (response) {this.$refs[0].$refs.game.structure = response.structure});
      },
      card_input: function(card_json) {
          axios.get('/game/move?gameid='+this.$refs[0].$refs.game.games+'&playerid='+this.$refs[0].$refs.game.curplayer+'&move='+card_json).then(
            function (response) {this.$refs[0].$refs.game.structure = response.structure});
            this.$refs[0].$refs.game.curplayer++;
            if(this.$refs[0].$refs.game.curplayer > 1){this.$refs[0].$refs.game.curplayer = 0};
      }
  }
})