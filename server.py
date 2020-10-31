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

connected_users={}

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
            game=database.Game(game_id=object_id)
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
            return redirect('/home')
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
    games=user.get_games()
    if len(games)>0:
        game_list="<ul>"
        for game in games:
            name=game[1]
            if name=="":
                name=str(game[0])
            game_list+="<li>"
            game_list+="<form action=\"/game/"+str(game[0])+"\" method=\"get\">"
            game_list+="<input type=\"submit\" value=\""+name+"\"></form></li>"
        game_list+="</ul>"
    else:
        game_list="You are not in any games"
    return render_template('home.html',NICKNAME=user.nickname,GROUP_LIST=group_list,PENDING_GROUPS=invite_list,GAMES=game_list,GROUP_TEXT=text)

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
        except Exception:
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
    games=group.load_games()
    if len(games)>0:
        game_list="<ul>"
        for game in games:
            name=game[1]
            if name=="":
                name=str(game[0])
            game_list+="<li>"
            game_list+="<form action=\"/game/"+str(game[0])+"\" method=\"get\">"
            game_list+="<input type=\"submit\" value=\""+name+"\"></form></li>"
        game_list+="</ul>"
    else:
        game_list="You are not in any games"
    game_temp_example='<form action="/game/start" method=post><input type="hidden" name="group_id" value="'+str(group.group_id)+'"><input type="hidden" name="game_type" value="avalon"><input type="submit" value="Make Avalon"></form'
    game_temp_example2='<form action="/game/start" method=post><input type="hidden" name="group_id" value="'+str(group.group_id)+'"><input type="hidden" name="game_type" value="charades"><input type="submit" value="Make Charades"></form'
    return render_template('group.html',GROUP_NAME=group.name,MEMBER_LIST=members,USER_LIST=invites,PAST_GAMES=game_list,GROUP_TEXT="",GAME_LIST=game_temp_example2)

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


@socketio.on('disconnect')
def remove_connection():
    if not 'username' in request.cookies:
        print("bye2")
        fs.disconnect(request.sid)
    user=load_user(request.cookies.get('username'))
    if not user:
        print("bye2")
        fs.disconnect(request.sid)
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        print("bye2")
        fs.disconnect(request.sid)
    if request.sid in connected_users:
        for game in connected_users[request.sid]:
            connected_users[request.sid][game].disconnect(user.username,request.sid)
        connected_users.pop(request.sid)
        
@socketio.on('connect')
def create_connection():
    print("socket connect")
    if not 'username' in request.cookies:
        print("bye1")
        fs.disconnect(request.sid)
    user=load_user(request.cookies.get('username'))
    if not user:
        print("bye1")
        fs.disconnect(request.sid)
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        fs.disconnect(request.sid)
    if request.sid not in connected_users:
        connected_users[request.sid]={}

@socketio.on('join')
def on_test(data):
    print("joining game?")
    if not 'username' in request.cookies:
        print("bye3")
        fs.disconnect(request.sid)
    user=load_user(request.cookies.get('username'))
    if not user:
        print("bye3")
        fs.disconnect(request.sid)
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        print("bye3")
        fs.disconnect(request.sid)
    if not 'game_id' in data:
        print("bye3")
        fs.disconnect(request.sid)
    print(data)
    session=load_session(data['game_id'])
    if not session:
        print("bye4")
        fs.disconnect(request.sid)
    group=load_group(session.group_id)
    if not group:
        print("bye5")
        fs.disconnect(request.sid)
    if not group.auth(user.username):
        print("bye5")
        fs.disconnect(request.sid)

    session.connect(user.username,request.sid)
    connected_users[request.sid][session.game_id]=session
    fs.emit('update',session.get_updates(-1,-1,user.username),room=request.sid)

@socketio.on('move')
def on_test(data):
    if not 'username' in request.cookies:
        fs.disconnect(request.sid)
        return
    user=load_user(request.cookies.get('username'))
    if not user or not 'password' in request.cookies or not user.auth(request.cookies.get('password')) or not 'game_id' in data:
        fs.disconnect(request.sid)
        return
    session=load_session(data['game_id'])
    if not session:
        fs.disconnect(request.sid)
        return
    group=load_group(session.group_id)
    if not group or not group.auth(user.username):
        fs.disconnect(request.sid)
        return
    if user.username not in session.rooms and request.sid not in session.rooms[user.username]:
        fs.disconnect(request.sid)
        return
    if 'move' not in data or 'data' not in data:
        fs.disconnect(request.sid)
    else:
        for (user,updates) in session.make_move(data['move'],data['data'],user.username).items():
            if user in session.rooms:
                for sid in session.rooms[user]:
                    fs.emit('update',updates,room=sid)
    

@app.route('/game/start',methods=['GET','POST'])
def create_game():
    if 'username' not in request.cookies:
        return redirect('/login')
    user=load_user(request.cookies.get('username'))
    if not user:
        return redirect('/login')
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        return redirect('/login')
    print("User auth")
    if request.method=='POST':
        argsdict=request.form
    elif request.method=='GET':
        argsdict=request.args
    else:
        argsdict={}
    print(argsdict)
    if 'game_type' not in argsdict:
        return redirect('/home')
    if 'group_id' not in argsdict:
        return redirect('/home')
    print("args good")
    group=load_group(argsdict['group_id'])
    if not group:
        return redirect('/home')
    if not group.auth(user.username):
        return redirect('/home')
    game_name=None
    print("group good")
    print(argsdict)
    if 'game_name' in argsdict:
        game_name=argsdict['game_name']
    try:
        session=database.Game(None,game_name,argsdict['game_type'],argsdict['group_id'],'Sessions/')
    except:
        return home_page("Failed to create game!")
    session.create_game(group.users)
    print(session.game_id,user.username)
    return redirect('/game/'+str(session.game_id))
    return render_template('game.html',game_id=session.game_id, player_id="'"+user.username+"'")


@app.route('/game/<int:game_id>',methods=['GET','POST'])
def join_game(game_id):
    #@app.route('/game')
    #def get_full_game_state():
    if 'username' not in request.cookies:
        return redirect('/login')
    user=load_user(request.cookies.get('username'))
    if not user:
        return redirect('/login')
    if not 'password' in request.cookies or not user.auth(request.cookies.get('password')):
        return redirect('/login')
    
    session=load_session(game_id)
    if not session:
        return redirect('/home')
    group=load_group(session.group_id)
    if not group:
        return redirect('/home')
    if not group.auth(user.username):
        return redirect('/home')

    return render_template('game.html',game_id=session.game_id, player_id="'"+user.username+"'")
