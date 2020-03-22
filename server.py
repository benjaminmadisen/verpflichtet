import pickle
import json
import TicTacToe
import urllib
from flask import Flask, Response, request, session, jsonify


filename="DoNotOpenPlease.jpg"
session_dir='/sessions'

sessions={}
users={}
groups={}
unsaved={'sessions':False,'users':False,'groups':False,'game_engines':False}
game_engines={'tictactoe':TicTacToe}

class Group:
    global unsaved
    def __init__(self):
        self.users=[]
        self.games=[]
        unsaved['groups']=True

    def add_user(self,username):
        self.users.append(username)
        unsaved['groups']=True

    def get_player_id(self,username):
        i=0
        for user in self.users:
            if(user==username):
                return i
            i+=1
        return -1
    
    def add_game(self,game_id):
        self.games.append(game_id)
        unsaved['groups']=True
    

class Game:
    global unsaved
        
    def get_player_id(self, username):
        print(username)
        print(groups[self.group_id].users)
        return groups[self.group_id].get_player_id(username)
    
    def get_group(self):
        return groups[self.group_id]
    
    def get_engine(self):
        return game_engines[self.engine_id]
    
    def make_move(self, move, data, player_id=-1):
        unsaved['sessions']=True
        return (self.get_engine()).update_with_move(self.name, move, data, player_id)

    def get_state(self, move, player_id=-1):
        return (self.get_engine()).get_after_move(self.name, move, player_id)

    def __init__(self, name, engine_id, group_id):
        self.name=name
        self.group_id=group_id
        self.engine_id=engine_id
        groups[group_id].add_game(self.name)
        self.done=False
        (self.get_engine()).init(name,self.get_group())
        unsaved['sessions']=True


app = Flask(__name__)
app.secret_key = 'ITS A SECRET TO EVERYBODY'


@app.route('/')
def hello_world():
    with open('static/index.html','r') as a:
        return a.read()

@app.route('/save')
def save_data():
    for key in unsaved:
        if(unsaved[key]):
            outfile=open(key+"_data",'wb')
            pickle.dump(eval(key),outfile)
            outfile.close()
            unsaved[key]=False
    return 'Pickled!'

@app.route('/load')
def load_data():
    global sessions,users,groups,game_engines
    for key in unsaved:
        infile=open(key+"_data",'rb')
        #eval(key)=pickle.load(infile)
        infile.close()
    return 'UnPickled!'

@app.route('/set', methods=['GET', 'POST'])
def set_data():
    output=''
    print(request.method)
    if request.method == 'GET':
        for key in request.args.keys():
            sessions[key]=request.args[key]
            output+='set ' + key + ' to ' + request.args[key] + '\n'
    return output

@app.route('/user', methods=['GET'])
def be_user():
    if request.method == 'GET':
        if('username' in request.args):
            session['username']=request.args['username']
            return 'logged in as ' + request.args['username']

@app.route('/me')
def who_am_i():
    return session['username']
    
@app.route('/group/<group_id>')
def get_group(group_id):
    if(group_id in groups):
        group=groups[group_id]
    else:
        group=Group()
        groups[group_id]=group
    if(session['username']):
        if(group.get_player_id(session['username']) == -1):
            group.add_user(session['username'])
    return str(group.users)
    
@app.route('/game/move', methods=['GET'])
def update_game():
    game_id=''
    move=-1
    player_id=-1
    data={}
    if request.method == 'GET':
        for field in request.args:
            if(field=='gameid'):
                game_id=request.args[field]
            elif(field=='move'):
                move=int(request.args[field])
            else:
                print(urllib.parse.unquote(request.args[field]))
                data[field]=urllib.parse.unquote(request.args[field])
    if(game_id==''):
        return 'Error: No game specified'
    if(move==-1):
        return 'Error: No move specified'
    print(sessions)
    game=sessions[game_id]
    if('username' not in session):
        return 'Error: Spectating not currently allowed'
    player_id=game.get_player_id(session['username'])
    
    if(data):
        #return Response(game.make_move, mimetype='application/json')
        return game.make_move(move,data,player_id)
    else:
        return Response(game.get_state, mimetype='application/json')
        #return game.get_state(move, player_id)
    

@app.route('/game/start')
def create_game():
    game_id=''
    engine_id=''
    group_id=''
    if request.method == 'GET':
        for field in request.args:
            if(field=='gameid'):
                game_id=request.args[field]
            elif(field=='type'):
                engine_id=request.args[field]
            elif(field=='groupid'):
                group_id=request.args[field]
    if(game_id==''):
        return 'Error: No id specified'
    if(group_id==''):
        return 'Error: No group specified'
    if(engine_id==''):
        return 'Error: No game specified'
    sessions[game_id]=Game(game_id, engine_id,group_id)
    return Response(sessions[game_id].get_state(0), mimetype='application/json')
    #return sessions[game_id].get_state(0)
    #return 'Game started successfully'

@app.route('/game')
def get_full_game_state():
    game_id=''
    player_id=-1
    if request.method == 'GET':
        for field in request.args:
            if(field=='gameid'):
                game_id=request.args[field]
    if(game_id==''):
        return 'Error: No game specified'
    game=sessions[game_id]
    if('username' not in session):
        return 'Error: Spectating not currently allowed'
    player_id=game.get_player_id(session['username'])
    return Response(game.get_state(0, player_id), mimetype='application/json')
    #return game.get_state(0, player_id)

@app.route('/show')
def show_data():
    return str(sessions)
