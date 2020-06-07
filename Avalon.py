import json
import pickle
import random
datapath="Avalon/"

loaded={}
players=[]
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

def init(path, player_names):
    player_order=player_names.copy()
    random.shuffle(player_order)
    #board=[["_", "_", "_"],["_", "_", "_"],["_", "_", "_"]]
    players=player_names
    state={'board':[],'history':[],'player_order':player_order,'turn':0}
    state['history']
    save_state(path,state)

def update_with_move(path, move, data, player_id):
    print(move,data,player_id)
    state=load_state(path)
    board=state['board']
    #x=int(data['x'])
    #y=int(data['y'])
    num_players=len(state['player_order'])
    output={}
    if(move<state['turn']):
        print("Can't make move that's already made!")
        output['username']={'updates':{'messageBox':{'id': 'messageBox', 'type': 'card', 'value': "Can't make move that's already made!", 'clickable':False, 'visible':True},0:{'objects':['messageBox']}}, 'turn': state['turn']}
        #output['username']['updates'][0]={'objects':['messageBox']}
        return output
    print(state['player_order'].index(player_id))
    print(move,state['turn'])
    if(state['turn'] % num_players!=state['player_order'].index(player_id)):
        print("this failed")
        output['username']={'updates':{'messageBox':{'id': 'messageBox', 'type': 'card', 'value': "It's not your turn!", 'clickable':False, 'visible':True},0:{'objects':['messageBox']}}, 'turn': state['turn']}
        #output['username']['updates'][0]={'objects':['messageBox']}
        return output

    print("hi from here")
    mydict={'testButton':{'id':'testButton', 'type': 'card', 'value': "It's not your turn!",'clickable':False, 'visible':True},0:{'objects':['testButton']}}
    nextdict={'testButton':{'id':'testButton', 'type': 'card', 'value': "Take a turn",'clickable':True, 'onclickjson':{}, 'visible':True},0:{'objects':['testButton']}}
    state['turn']+=1

    next_player=state['player_order'][(state['turn']) % num_players]
    print(next_player)
    output[next_player]={'updates':nextdict,'turn': state['turn']}
    for player in state['player_order']:
        if player!=next_player:
            output[player]={'updates':mydict,'turn':state['turn']}
    state['history'].append(player_id+' pressed the button')
    save_state(path,state)
    print(state['history'])
    return output

def get_state_updates(path, start_move, end_move, player_id):
    state=load_state(path)
    history=state['history']
    if end_move==-1:
        move=state['turn']
    else:
        move=end_move
    num_players=len(state['player_order'])
    if(move % num_players)!=state['player_order'].index(player_id):

        mydict={'testButton':{'id':'testButton', 'type': 'card', 'value': "It's not your turn!",'clickable':False, 'visible':True}, 0:{'objects':['testButton']}}
    else:
        if move<state['turn']:
            mydict={'testButton':{'id':'testButton', 'type': 'card', 'value': "This was your turn",'clickable':False, 'visible':True}, 0:{'objects':['testButton']}}
        else:
            mydict={'testButton':{'id':'testButton', 'type': 'card', 'value': "Take a turn",'clickable':True, 'onclickjson':{}, 'visible':True}, 0:{'objects':['testButton']}}
    
    return {'updates':mydict,'turn':state['turn']}
