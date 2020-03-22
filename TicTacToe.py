import json
import pickle
dirpath="Sessions/TicTacToe/"

loaded={}

def save_state(name, state):
    outfile=open(dirpath+name,'wb')
    pickle.dump(state,outfile)
    outfile.close()
    
def load_state(name):
    global loaded
    if(name not in loaded):
        infile=open(dirpath+name,'rb')
        state=pickle.load(infile)
        infile.close()
        loaded[name]=state
    else:
        state=loaded[name]
    return state

def init(name, group):
    board=[[" ", " ", " "],[" ", " ", " "],[" ", " ", " "]]
    

    state={'board':board,'history':[]}
    save_state(name,state)

def update_with_move(name, move, data, player_id):
    state=load_state(name)
    board=state['board']
    x=int(data['x'])
    y=int(data['y'])
    
    if(move<len(state['history'])):
        return "Error: Move already made"
    print(player_id)
    if ((move+1)%2 != player_id):
        return "Error: Wrong player!"
    if(board[x][y]!=" "):
        return "Error: Already filled!"
    if(player_id==0):
        board[x][y]="X"
    if(player_id==1):
        board[x][y]="O"
    print(state)
    state['board']=board
    state['history'].append((x,y))
    save_state(name,state)
    return get_after_move(name, move, player_id)

def get_after_move(name, move, player_id):
    state=load_state(name)
    history=state['history']
    if ((move+1)%2 == player_id):
        phasing=True
    else:
        phasing=False
    return get_full_config_from_board(state['board'],phasing,len(state['history']))
    
    
def get_full_config_from_board(board, phasing,move,message=""):
    outjson={'updates':{},'turn':move+1}
    uid=0
    for i in range(3):
        stuff={}
        for j in range(3):
            clickable=True
            if(board[i][j]!=" "):
                clickable=False
            if(not phasing):
                clickable=False
            outjson['updates'][uid]={'id': uid, 'type': 'card', 'value': str(board[i][j]), 'clickable': str(clickable).lower(), 'onclickjson': {"x":str(i),"y":str(j)}, 'visible':True}
            #stuff.append({'id': str(uid), 'type': 'card', 'value': str(board[i][j]), 'clickable': str(clickable).lower(), 'onclickjson': {"x":str(i),"y":str(j)}, 'visible':True})
            uid+=1
        outjson['updates'][uid]={'id': uid, 'type':'container', 'objects': list(range(uid-3,uid)), 'visible':True}
        uid+=1
    outjson['updates'][str(uid)]={'id': str(uid), 'type':'container', 'objects': [uid+1], str(uid+1):{'id': uid+1, 'type': 'card', 'value': message, 'clickable': str(False).lower(), 'visible':True}, 'visible':True}
    print(json.dumps(outjson))
    return json.dumps(outjson)
