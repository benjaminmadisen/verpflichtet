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
        games: 0,
        curplayer: 0,
        turn: 0,
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
        this.$children[0].games++;
        var game=this;
        console.log(this.$children[0]);
        axios.get('/game/start?groupid=1&type=tictactoe&gameid='+this.$children[0].games).then(
            function (response) {console.log(response.data); console.log(game.$children[0]); game.$children[0].structure.objects = response.data.updates; game.$children[0].turn=response.data.turn;});
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
            function (response) {this.$children[0].structure = response.structure});
            this.$children[0].curplayer++;
            if(this.$children[0].curplayer > 1){this.$children[0].curplayer = 0};
      }
  }
})
