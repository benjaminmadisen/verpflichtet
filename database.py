import pickle
import threading
import sqlite3
import TicTacToe
import Avalon
import Charades

game_engines={'tictactoe':TicTacToe,'avalon':Avalon,'charades':Charades}

CORE_DB_PATH="mainDB.sql"


def connect_database(path):
    """
    Connect to the sqlite database at path
    """
    connection = None
    if path is None:
        return None
    try:
        connection = sqlite3.connect(path)
        #print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def init_database(db):
    """
    Initialize an sqlite database to keep track of probes that have run, if one doesn't exist
    """
    cursor = db.cursor()
    tables_schema = {}
    tables_schema['users'] = {'username':'TEXT','nickname':'TEXT','password':'TEXT','PRIMARY KEY': 'username ASC'}
    #'CREATE TABLE probes(id INTEGER, type TEXT, name TEXT, create_time INTEGER, start_time INTEGER, end_time INTEGER, PRIMARY KEY(id ASC));'
    tables_schema['groups'] = {'id':'INTEGER','name':'TEXT', 'PRIMARY KEY': 'id ASC'}
    #'CREATE TABLE probe_inputs(probe_id INTEGER, name TEXT, value TEXT);'
    tables_schema['sessions'] = {'id':'INTEGER','name':'TEXT','group_id':'INTEGER', 'engine':'TEXT','state':'INTEGER','datapath':'TEXT', 'PRIMARY KEY': 'id ASC'}
    #'CREATE TABLE probe_outputs(probe_id INTEGER, errors TEXT, output TEXT);'
    tables_schema['user_groups'] = {'id':'INTEGER','group_id':'INTEGER','username':'TEXT','status':'INTEGER','PRIMARY KEY': 'id ASC'}
    for table_name in tables_schema:
        print("Checking table " + table_name)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        res = cursor.fetchone()
        if res is None:
            print("Adding table " + table_name)
            query="CREATE TABLE "+table_name+"("
            for i in tables_schema[table_name]:
                if not i=="PRIMARY KEY":
                    query+=i+' '+tables_schema[table_name][i]+','
                else:
                    query+=i+'('+tables_schema[table_name][i]+'));'
            cursor.execute(query)
            db.commit()
    db.close()

db=connect_database(CORE_DB_PATH)
init_database(db)

def flush_database():
    db=connect_database(CORE_DB_PATH)
    if not db:
        raise(Exception("Could Not Connect To Database"))
    cursor=db.cursor()
    cursor.execute("DROP TABLE users;")
    cursor.execute("DROP TABLE groups;")
    cursor.execute("DROP TABLE sessions;")
    cursor.execute("DROP TABLE user_groups;")
    db.commit()

class User:
    def __init__(self,username,password=None):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        print("SELECT * FROM users WHERE username=?;",(username,))
        cursor.execute("SELECT * FROM users WHERE username=?;",(username,))
        res=cursor.fetchone()
        if not res:
            if password:
                cursor.execute("INSERT INTO users (username, nickname, password) VALUES (?,?,?);",(username,username,password))
                db.commit()
            cursor.execute("SELECT username,nickname FROM users WHERE username=?;",(username,))
            res=cursor.fetchone()
        else:
            if password:
                raise(Exception("Username Taken"))
        if not res:
            raise(Exception("User Not Found Or Created"))
        self.username=res[0]
        self.nickname=res[1]
        db.close()
    
    def auth(self,password):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?;",(self.username,password))
        res=cursor.fetchone()
        if res:
            db.close()
            return True
        db.close()
        return False
    
    def get_groups(self,status=2):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        print("hereish")
        results=[]
        for result in cursor.execute("SELECT groups.id, groups.name FROM users INNER JOIN user_groups ON user_groups.username=users.username INNER JOIN groups ON user_groups.group_id=groups.id WHERE user_groups.status = ? AND users.username= ?;",(status,self.username)):
            print(result)
            results.append((result[0],result[1]))
        db.close()
        return results
    
    def get_games(self):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        cursor.execute("SELECT DISTINCT sessions.id, sessions.name, sessions.state FROM users INNER JOIN user_groups ON user_groups.username=users.username INNER JOIN sessions ON user_groups.group_id=sessions.group_id ORDER BY sessions.id DESC")
        results=[]
        for result in cursor:
            results.append((result[0],result[1],result[2]))
        db.close()
        return results

class Group:
    def __init__(self,name=None,group_id=None):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        if not group_id:
            if not name:
                raise(Exception("Group Needs a Name"))
            print("hi")
            cursor.execute("INSERT INTO groups (id, name) VALUES (NULL, ?);",(name,))
            db.commit()
            cursor.execute("SELECT id,name FROM groups WHERE name=? ORDER BY id DESC LIMIT 1;",(name,))
            res=cursor.fetchone()
        else:
            query="SELECT * FROM groups WHERE "
            if name: 
                query+= "name='"+name+"' AND "
            query+="id="+str(group_id)+";"

            cursor.execute(query)
            res=cursor.fetchone()
        if not res:
            print("Nope")
            raise(Exception("Group Not Found"))
        print("hi again")
        self.group_id=res[0]
        self.name=res[1]
        self.users=[]
        self.games=[]
        self.load_users()
        db.close()

    def load_users(self):
        print("loading users")
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        for row in cursor.execute("SELECT username FROM user_groups WHERE group_id= ? AND status > 1 ORDER BY id;",(self.group_id,)):
            self.users.append(row[0])
        db.close()

    def add_user(self,username,state=1):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        if state>0:
            print(type(self.group_id))
            cursor.execute("SELECT id FROM user_groups WHERE group_id=? AND username=?;",(self.group_id,username))
            res=cursor.fetchone()
            entry_id=None
            if res:
                entry_id=res[0]
            print(res)
            #print("REPLACE INTO user_groups (id, group_id, username, status) VALUES (NULL,"+str(self.group_id)+",'"+username+"',"+str(state)+");")
            cursor.execute("REPLACE INTO user_groups (id, group_id, username, status) VALUES (?,?,?,?);",(entry_id,self.group_id,username,state))
            db.commit()
        if state>1:
            self.users.append(username)
        db.close()
        #TODO: Implement deletion
        
    def get_player_id(self,username):
        i=0
        for user in self.users:
            if(user==username):
                return i
            i+=1
        return -1
    
    def auth(self, username):
        if username in self.users:
            return True
        return False
    
    def get_users(self, status=2):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        out=[]
        for row in cursor.execute("SELECT username FROM user_groups WHERE group_id= ? AND status= ? ORDER BY id;",(self.group_id,status)):
            out.append(row[0])
        print("here")
        db.close()
        return out

    def load_games(self, minstate=0):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        for row in cursor.execute("SELECT id, name FROM sessions WHERE group_id= ? AND state > ? ORDER BY id DESC;",(self.group_id,minstate)):
            if (row[0],row[1]) not in self.games:
                self.games.append((row[0],row[1]))
        db.close()
        return self.games

    def get_all_other_users(self):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        ret=[]
        for row in cursor.execute("SELECT username FROM users;"):
            if row[0] not in self.users:
                ret.append(row[0])
        return ret

class Game:
    def get_engine(self):
        return game_engines[self.engine_id]
    
    def make_move(self, move, data, player_id=None):
        return (self.get_engine()).update_with_move(self.datapath, move, data, player_id)

    def get_updates(self, start_move, end_move, player_id=None):
        return (self.get_engine()).get_state_updates(self.datapath, start_move,end_move,player_id)


    def get_state(self, move, player_id=None):
        return (self.get_engine()).get_after_move(self.name, move, player_id)

    def __init__(self, game_id=None, name=None, engine_id=None, group_id=None, datapath=None):
        db=connect_database(CORE_DB_PATH)
        if not db:
            raise(Exception("Could Not Connect To Database"))
        cursor=db.cursor()
        if not game_id:
            if not (engine_id and group_id and datapath):
                raise(Exception("Invalid Engine Or Group For Game"))
            cursor.execute("INSERT INTO sessions (id, name, group_id, engine, state, datapath) VALUES (NULL, NULL,?,?,1,NULL);",(group_id,engine_id))
            db.commit()
            new_id=cursor.lastrowid
            cursor.execute("SELECT id FROM sessions WHERE id="+str(new_id)+";")
            res=cursor.fetchone()
            if not res:
                raise(Exception("Session Not Created"))
            if not name:
                name=str(res[0])
            self.datapath=datapath+game_engines[engine_id].datapath+str(res[0])+"_"+name
            cursor.execute("REPLACE INTO sessions (id, name, group_id, engine, state, datapath) VALUES (?,?,?,?,1,?);",(res[0],name,group_id,engine_id,self.datapath))
            db.commit()
            cursor.execute("SELECT id, name, group_id, engine, state, datapath FROM sessions WHERE id= ?;",(res[0],))
            res=cursor.fetchone()
        else:
            cursor.execute("SELECT id, name, group_id, engine, state, datapath FROM sessions WHERE id= ?;",(game_id,))
            res=cursor.fetchone()
        if not res:
                raise(Exception("Session Not Found"))

        self.game_id=res[0]
        self.name=res[1]
        self.group_id=res[2]
        self.engine_id=res[3]
        self.state=res[4]
        self.datapath=res[5]
        self.rooms={}
        db.close()
    
    def connect(self,username,sid):
        if username not in self.rooms:
            self.rooms[username]=[sid]
        elif sid not in self.rooms[username]:
            self.rooms[username].append(sid)
    
    def disconnect(self,username,sid):
        if username in self.rooms:
            if sid in self.rooms[username]:
                self.rooms[username].remove(sid)
            if len(self.rooms[username])==0:
                self.rooms.pop(username)
    
    def create_game(self,players):
        (self.get_engine()).init(self.datapath,players)




