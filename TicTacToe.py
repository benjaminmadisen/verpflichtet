dirpath="Sessions/TicTacToe/"

loaded={}

def save_state(name, state):
    outfile=open(dirpath+name,'wb')
    pickle.dump(state,outfile)
    outfile.close()
    
def load_state(name):
    if(name not in loaded):
        infile=open(dirpath+name,'rb')
        state=pickle.load(infile)
        infile.close()
    loaded[name]=state
    return state

def init(name, group):
    board=[[" ", " ", " "],[" ", " ", " "],[" ", " ", " "]]
    state={'board':board,'history':[]}
    save_state(state)

def make_move(name, move, data, player_id):
    state=load_state(name)
    board=state['board']
    x=data['x']
    y=data['y']
    
    if(move<=len(state['history'])):
        return "Error: Move already made"
    if ((move+1)%2 == player_id):
        return "Error: Wrong player!"
    if(board[x][y]!=" "):
        return "Error: Already filled!"
    if(player_id==0):
        board[x][y]="X"
    if(player_id==1):
        board[x][y]="O"
    state[board]=board
    save_state(name,state)

def get_after_move(name, move, player_id):
    state=load_state(name)
    history=state['history']
    toSend=history[move+1:]
    
