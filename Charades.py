import random
import pickle
import json
datapath="Charades/"

loaded={}

def save_state(name, state):
    outfile=open(name,'wb')
    pickle.dump(state,outfile)
    outfile.close()
    
def load_state(name):
    global loaded
    if(name not in loaded):
        infile=open(name,'rb')
        state=pickle.load(infile)
        infile.close()
        loaded[name]=state
    else:
        state=loaded[name]
    return state

class Charades:

    def __init__(self,players):
        self.players=players
        self.host=self.players[0]
        self.words=[]
        self.guesser=0
        self.rules={"point":"guesser","nextGuesser":"list","replaceWords":False,"endOn":"words"}
        self.phase="setup"
        self.player_words={}
        self.comparewords=[]
        self.waiting={}
        self.currentword=0
        self.player_order=[]
        self.scores={}
        for player in self.players:
            self.player_words[player]=[]
            self.waiting[player]=False
            self.scores[player]=0
        return


    def display(self,move,player_id):
        updates={}
        if self.phase=="setup":
            if not self.waiting[player_id]:
                updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "Add words or phrases for the game", 'clickable':False, 'visible':True}
                updates['typingBox']= {'id': 'typingBox', 'type': 'text_box','onclickjson':{"type":"add_word"}}
                updates['readyButton']={'id':'readyButton','type':'card','value':'Submit Words','clickable':True,'onclickjson':{'type':'waiting'},'style':{'display': 'inline-block', 'float':'left'}}
                number=0
                wordlist=[]
                for word in self.player_words[player_id]:
                    updates['line'+str(number)]={'id': 'line'+str(number), 'type': 'container', 'objects':['word'+str(number),'removeword'+str(number)],'style':{'width': '100%','display': 'block', 'float':'left'}}
                    updates['word'+str(number)]={'id':'word'+str(number),'type':'card','value':word,'clickable':False,'style':{'display': 'inline-block', 'float':'left'}}
                    updates['removeword'+str(number)]={'id':'removeword'+str(number),'type':'card','value':'X','clickable':True,'onclickjson':{'type':'remove_word','name':word},'style':{'display': 'inline-block', 'float':'left'}}
                    wordlist.append('line'+str(number))
            #wordlist.append('removeword'+str(number))
                    number+=1
                updates['wordList']={'id': 'wordList', 'type': 'container', 'objects':wordlist}
                updates[0]={'id': 0, 'type':'container', 'objects':['messageBox','typingBox','wordList','readyButton']}
            else:
                updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "Waiting for other players to submit words", 'clickable':False, 'visible':True}
                updates[0]={'id': 0, 'type':'container', 'objects':['messageBox']}
        if self.phase=="playing":
            if player_id==self.player_order[self.guesser]:
                updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "Your word is:", 'clickable':False, 'visible':True,'style':{'width':'100%', 'display': 'block', 'text-align': 'center'}}
                updates['wordBox']={'id': 'wordBox', 'type': 'card', 'value': self.words[self.currentword], 'clickable':False, 'visible':True,'style':{'width':'100%', 'display': 'block', 'text-align': 'center','font-size': '40px','height':'10%','float':'center'}}
                updates['skipButton']={'id':'skipButton','type':'card','value':'Skip','clickable':True,'onclickjson':{'type':'skip'},'style':{'width':'50%','height':'10%','font-size':'20px'}}
                updates['scoreButton']={'id':'scoreButton','type':'card','value':'Next word','clickable':True,'onclickjson':{'type':'next_word','person':player_id},'style':{'width':'50%','height':'10%','font-size':'20px'}}
                updates['buttonBox']={'id':'buttonBox','type':'container','objects':['skipButton','scoreButton'],'style':{'width':'40%', 'display': 'block', 'margin': 'auto'}}
                updates['nextButton']={'id':'nextButton','type':'card','value':'Next person','clickable':True,'onclickjson':{'type':'next_player'}}
                updates[0]={'id': 0, 'type':'container', 'objects':['messageBox','wordBox','buttonBox','nextButton']}
            else:
                updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': self.player_order[self.guesser]+" is giving clues now!", 'clickable':False, 'visible':True,'style':{'width':'100%', 'display': 'block', 'text-align': 'center'}}
                updates[0]={'id': 0, 'type':'container', 'objects':['messageBox']}
        output={player_id:{'updates':updates}}
        return output

    def change_phase(self,move):
        output={}
        if self.phase=="playing":
            print(self.guesser)
            person=self.player_order[self.guesser]
            nonguesser={}
            guesser={}
            nonguesser['messageBox']={'id': 'messageBox', 'type': 'card', 'value': person+" is giving clues now!", 'clickable':False, 'visible':True,'style':{'width':'100%', 'display': 'block', 'text-align': 'center'}}
            nonguesser[0]={'id': 0, 'type':'container', 'objects':['messageBox']}
            guesser=self.display(move,person)[person]['updates']
            for player in self.players:
                print(player)
                print(person)
                if player==person:
                    output[player]={'updates':guesser}
                else:
                    output[player]={'updates':nonguesser}
        if self.phase=="setup":
            for player in self.players:
                output[player]={'updates':self.display(move,player)[player]['updates']}
        return output
    
    def update(self,move,data,player_id):
        print(data)
        if self.phase=="setup":
            if data['type']=="add_word":
                if 'value' in data:
                    word=data['value']
                    test=word.lower().replace(" ","")
                    if test not in self.comparewords:
                        self.comparewords.append(test)
                        self.player_words[player_id].append(word)
                    else:
                        print("Word already added")
            if data['type']=="remove_word":
                if 'name' in data:
                    word=data['name']
                    test=word.lower().replace(" ","")
                    self.comparewords.remove(test)
                    self.player_words[player_id].remove(word)
            if data['type']=="waiting":
                self.waiting[player_id]=True
                ready=True
                for person in self.waiting:
                    print(person)
                    if not self.waiting[person]:
                        ready=False
                print(ready)
                if ready:
                    print("ready")
                    self.phase="playing"
                    self.player_order=list(self.waiting.keys())

                    self.words=[]
                    for player in self.player_words:
                        self.words.extend(self.player_words[player])
                    random.shuffle(self.words)
                    random.shuffle(self.player_order)
                    print(self.player_order)
                    print(self.player_order[0])
                    self.guesser=0
                    self.currentword=0
                    return self.change_phase(move)

        if self.phase=="playing":
            if data['type']=="next_player":
                
                if self.rules['nextGuesser']=="list":
                    self.guesser+=1
                    if self.guesser>=len(self.player_order):
                        if self.rules['endOn']=="players":
                            self.phase="setup"
                            for player in self.players:
                                self.waiting[player]=False
                            return self.change_phase(move)
                        else:
                            self.guesser=0
                return self.change_phase(move)
            if data['type']=="skip":
                self.words.append(self.words[self.currentword])
                self.words.pop(self.currentword)
                return self.display(move,player_id)
            if data['type']=="next_word":
                self.currentword+=1
                self.scores[data['person']]+=1
                if self.currentword>=len(self.words):
                    if self.rules['endOn']=="words":
                        self.phase="setup"
                        for player in self.players:
                            self.waiting[player]=False
                        return self.change_phase(move)
                    else:
                        self.currentword=0
                return self.display(move,player_id)
        return self.display(move,player_id)

def get_after_move(path, move, player_id):
    state=load_state(path)
    game=state['board']
    return game.display(move,player_id)

def update_with_move(path, move, data, player_id):
    state=load_state(path)
    game=state['board']
    out=game.update(move,data,player_id)
    state['board']=game
    save_state(path,state)
    return out

def get_state_updates(path, start_move, end_move, player_id):
    state=load_state(path)
    game=state['board']
    return game.display(end_move,player_id)[player_id]

def init(path, player_names):
    player_order=player_names.copy()
    state={'board':Charades(player_order),'player_order':player_order,'turn':0}
    save_state(path,state)

