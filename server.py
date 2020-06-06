import pickle
import json
import urllib
import database
import os
import hashlib
from flask import *
import flask_socketio as fs


content_dir = os.path.abspath('static')
session_dir='/sessions'

caches={"session":{},"user":{},"group":{}}


def load(object_type,object_id):
    if object_type not in caches:
        return None
    if object_id in caches[object_type]:
        return caches[object_type][object_id]
    if object_type=="user":
        try:
            user=database.User(object_id)
            caches[object_type][object_id]=user
            return user
        except:
            return None
    if object_type=="group":
        try:
            group=database.Group(group_id=object_id)
            caches[object_type][object_id]=group
            return group
        except:
            return None
    if object_type=="session":
        try:
            game=database.Game(name=object_id)
            caches[object_type][object_id]=game
            return game
        except:
            return None
    return None
    
    
    
def load_user(username):
    return load("user",username)

def load_group(group_id):
    return load("group",group_id)

def load_session(session_id):
    return load("session",session_id)



app = Flask(__name__,template_folder=content_dir)
app.secret_key = 'ITS A SECRET TO EVERYBODY'
print("hi")
socketio = fs.SocketIO(app)
@app.route('/')
def hello_world():
    with open('static/index.html','r') as a:
        return a.read()

@app.route('/set', methods=['GET', 'POST'])
def set_data():
    output=''
    print(request.method)
    if request.method == 'GET':
        for key in request.args.keys():
            sessions[key]=request.args[key]
            output+='set ' + key + ' to ' + request.args[key] + '\n'
    return output

@app.route('/login')
def login_page():
    return render_template('login.html', LOGIN_TEXT="")

@app.route('/user', methods=['GET','POST'])
def be_user():
    print(request.method)
    if request.method == 'POST':
        print(request.form)
        print(request.data)
        if('username' in request.form and request.form['username']!=''):
            user=load_user(request.form['username'])
            print(user)
            if not user:
                try:
                    user=database.User(request.form['username'], hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest())
                except:
                    return render_template('login.html',LOGIN_TEXT="Could not create user!")
            
            resp = make_response(redirect('/user'))#make_response('Logging in as ' + request.form['username'])
            resp.set_cookie('username', request.form['username'])
            resp.set_cookie('password', hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest())
            #session['username']=request.args['username']
            return resp
            #except:
            #    return "Could not create user!"
        else:
            return render_template('login.html',LOGIN_TEXT="No username provided!")
    elif('username' in request.cookies):
        user=load_user(request.cookies.get('username'))
        if user:
            if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
                print("No password for you!")
                resp = make_response(render_template('login.html',LOGIN_TEXT="Invalid Password"))
                resp.set_cookie('username', '', expires=0)
                resp.set_cookie('password', '', expires=0)
                return resp
            print("Huh?")
            return "Logged in as " + request.cookies.get('username')
        else:
            return redirect('/login')
    else:
        return redirect('/login')

@app.route('/me')
def who_am_i():
    return request.cookies.get('username')
    
@app.route('/home')
def home_page(text=""):
    if 'username' not in request.cookies:
        return redirect('/login')
    user=load_user(request.cookies.get('username'))
    if not user:
        return redirect('/login')
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        return redirect('/login')
    groups=user.get_groups(2)
    if len(groups)>0:
        group_list="<ul>"
        for group in groups:
            if group[1]=="":
                group[1]=str(group[0])
            group_list+="<li><form action=\"/group/"+str(group[0])+"\" method=\"get\"><input type=\"submit\" value=\""+group[1]+"\"></form></li>"
        group_list+="</ul>"
    else:
        group_list="You are not in any groups"
    invites=user.get_groups(1)
    if len(invites)>0:
        invite_list="<ul>"
        for group in invites:
            if group[1]=="":
                group[1]=str(group[0])
            invite_list+="<li>"
            invite_list+="<form action=\"/join_group"+"\" method=\"post\">"
            invite_list+="<input type=\"hidden\" name=\"group_id\" value=\""+str(group[0])+"\">"
            invite_list+="<input type=\"hidden\" name=\"new_status\" value=\""+str(2)+"\">"
            invite_list+="<input type=\"submit\" value=\""+group[1]+"\"></form></li>"
        invite_list+="</ul>"
    else:
        invite_list="You have no invites"
    return render_template('home.html',NICKNAME=user.nickname,GROUP_LIST=group_list,PENDING_GROUPS=invite_list,GAMES="c",GROUP_TEXT=text)

@app.route('/group', methods=['GET','POST'])
def group_page():
    if 'username' not in request.cookies:
        return redirect('/login')
    user=load_user(request.cookies.get('username'))
    if not user:
        return redirect('/login')
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        return redirect('/login')
    if request.method=='POST':
        if 'groupname' not in request.form:
            return home_page("Can't create group, no name!")
        try:
            group=database.Group(name=request.form['groupname'])
        except:
            return home_page("Failed to create group!")
        group.add_user(user.username,2)
        return redirect('/group/'+str(group.group_id))
    if request.method=='GET':
        if 'id' not in request.args:
            return home_page("No group specified")
        else:
            return get_group(request.args['id'])
        return "Not implemented"

@app.route('/group/<group_id>')
def get_group(group_id):
    if 'username' not in request.cookies:
        return redirect('/login')
    user=load_user(request.cookies.get('username'))
    if not user:
        return redirect('/login')
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        return redirect('/login')
    group=load_group(group_id)
    if not group:
        return redirect('/home')
    if not group.auth(user.username):
        return redirect('/home')
    members=""
    if len(group.users)>0:
        members="<ul>"
        for member in group.users:
            members+="<li>"+member+"</li>"
        members+="</ul>"
    invites=""
    others=group.get_all_other_users()
    if len(others)>0:
        invites="<ul>"
        for username in others:
            invites+="<li>"
            invites+="<form action=\"/join_group"+"\" method=\"post\">"
            invites+="<input type=\"hidden\" name=\"group_id\" value=\""+str(group.group_id)+"\">"
            invites+="<input type=\"hidden\" name=\"new_status\" value=\""+str(1)+"\">"
            invites+="<input type=\"hidden\" name=\"username\" value=\""+username+"\">"
            invites+="<input type=\"submit\" value=\""+username+"\"></form></li>"
        invites+="</ul>"
    
    return render_template('group.html',GROUP_NAME=group.name,MEMBER_LIST=members,USER_LIST=invites,PAST_GAMES="c",GROUP_TEXT="",GAME_LIST="d")

@app.route('/temp')
def temp():
    return render_template('game.html',game_id=0,player_id=0)

@app.route('/join_group', methods=['POST'])
def add_to_group():
    print("hi1")
    if 'username' not in request.cookies:
        return redirect('/login')
    user=load_user(request.cookies.get('username'))
    if not user:
        return redirect('/login')
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        return redirect('/login')
    if 'group_id' not in request.form:
        return redirect('/home')
    group=load_group(request.form['group_id'])
    print("hi2")
    if not group:
        return redirect('/home')
    if 'new_status' not in request.form:
        return redirect('/home')
    if request.form['new_status']=="2":
        if user.username in group.get_users(1) and user.username not in group.users:
            group.add_user(user.username,2)
            return redirect('/group/'+str(group.group_id))
        return redirect('/home')
    elif request.form['new_status']=="1":
        if not group.auth(user.username):
            return redirect('/home')
        if 'username' not in request.form:
            return redirect('/group/'+str(group.group_id))
        if request.form['username'] in group.get_users(1):
            return redirect('/group/'+str(group.group_id))
        group.add_user(request.form['username'],1)
        return redirect('/group/'+str(group.group_id))


@socketio.on('test')
def on_test(data):
    print("here\n\n\n")
    print(request)
    print(request.cookies)
    print(data.keys())
    #if not 'username' in request.cookies:
    #    fs.disconnect(request.sid)
    #if request.cookies['username']!='david':
    #    fs.disconnect(request.sid)
    print("emit")
    fs.emit('customEmit',"",broadcast=True)

@socketio.on('create')
def on_test(data):
    print("here\n\n\n")
    print(request)
    print(request.cookies)
    

@socketio.on('join')
def on_test(data):
    print("here\n\n\n")
    print(request)
    print(request.cookies)

@socketio.on('move')
def on_test(data):
    print("here\n\n\n")
    print(request)
    print(request.cookies)

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
    if('username' not in request.cookies):
        return 'Error: Spectating not currently allowed'
    player_id=game.get_player_id(request.cookies.get('username'))
    
    if(data):
        #return Response(game.make_move, mimetype='application/json')
        return game.make_move(move,data,player_id)
    else:
        return Response(game.get_state(move,player_id), mimetype='application/json')
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
        game_id='NULL'
    if(group_id==''):
        return 'Error: No group specified'
    if(engine_id==''):
        return 'Error: No game specified'

    sessions[game_id]=Game(None, engine_id,group_id,game_id)
    if('username' in request.cookies):
        player_id=sessions[game_id].get_player_id(request.cookies.get('username'))
    else:
        player_id=-1
    return Response(sessions[game_id].get_state(0,player_id), mimetype='application/json')
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
    if('username' not in request.cookies):
        return 'Error: Spectating not currently allowed'
        
    player_id=game.get_player_id(request.cookies.get('username'))
    return render_template('game.html',game_id=game_id, player_id=player_id)
    #return Response(game.get_state(0, player_id), mimetype='application/json')
    #return game.get_state(0, player_id)

@app.route('/show')
def show_data():
    return str(sessions)
