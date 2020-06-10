import json
import pickle
import random
datapath="Avalon/"

loaded={}
players=[]
missions={5:[(2,1),(3,1),(2,1),(3,1),(3,1)],
    6:[(2,1),(3,1),(4,1),(3,1),(4,1)],
    7:[(2,1),(3,1),(3,1),(4,2),(4,1)],
    8:[(3,1),(4,1),(4,1),(5,2),(5,1)],
    9:[(3,1),(4,1),(4,1),(5,2),(5,1)],
    10:[(3,1),(4,1),(4,1),(5,2),(5,1)],
    2:[(1,1),(2,1),(2,1),(2,1),(2,1)]
    }
    
role_descriptors={'merlin':{'name':'Merlin','goal':'You must succeed 3 missions, and not get killed by the assassin'},
    'minions':{'name':'a minion of Mordred','goal':'You must fail 3 missions or kill Merlin'},
    'good':{'name':'a loyal servant of Arthur','goal':'You must succeed 3 missions, and keep Merlin from dying'},
    'morgana':{'name':'Morgana','goal':'You are on the evil side, but appear as Merlin to Percival'},
    'percival':{'name':'Percival','goal':'You must succeed 3 missions. You know the identity of Merlin, protect him!'},
    'assassin':{'name':'The Assassin','goal':'You must fail 3 missions, or correctly guess the identity of Merlin at the end'},
    'mordred':{'name':'Mordred','goal':'You are evil, but are unknown to Merlin'},
    'oberon':{'name':'Oberon','goal':'You are evil, but do not know any other evil characters'},
    'Spectator': {'name':'a spectator','goal':'Just watch and have a good time!'}}

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
    state={'board':Avalon(player_order),'player_order':player_order,'turn':0}
    save_state(path,state)



class Avalon:

    def start(self):
        i=0
        random.shuffle(self.players)
        temp=self.players.copy()
        self.king=self.players[0]
        random.shuffle(temp)
        if self.assassin:
            self.roles['assassin'].append(temp[i])
            i+=1
            self.evil+=1
        if self.mordred:
            self.roles['mordred'].append(temp[i])
            i+=1
            self.evil+=1
        if self.oberon:
            self.roles['oberon'].append(temp[i])
            i+=1
            self.evil+=1
        if self.morgana:
            self.roles['morgana'].append(temp[i])
            i+=1
            self.evil+=1
        if self.merlin:
            self.roles['merlin'].append(temp[i])
            i+=1
        if self.percival:
            self.roles['percival'].append(temp[i])
            i+=1
        max_evil=2
        if(len(players)<5):
            max_evil=1
        if(len(players)>6):
            max_evil=3
        if(len(players)>8):
            max_evil=4
        while(self.evil<max_evil):
            self.roles['minions'].append(temp[i])
            self.evil=self.evil+1
            i=i+1
        while i<len(players):
            self.roles['good'].append(temp[i])
            i+=1
        self.waiting=[self.king]
        self.phase="team_select"
        self.missions=missions[len(self.players)]
        self.toRun.append(self.team_select_setup)
        self.args.append({})
        print(self.roles)
        return self.setup_game()

    def __init__(self,players):
        #self.phase="team_select"
        self.phase="lobby"
        self.assassin=True
        self.mordred=False
        self.oberon=False
        self.merlin=True
        self.morgana=False
        self.percival=False
        
        self.history={}
        self.turn=0
        self.people=players.copy()
        self.king=players[0]
        self.players=players.copy()
        self.evil=0
        self.roles={'minions':[],'good':[],'assassin':[],'mordred':[],'morgana':[],'oberon':[],'merlin':[],'percival':[]}
        self.missions=missions[len(self.players)]
        self.mission_history=[]
        self.current_mission=0
        self.fails=0
        self.succeeds=0
        self.vote_count=0
        self.team=[]
        self.votes={}
        self.waiting=self.people.copy()
        self.toRun=[]
        self.args=[]


    def get_card(self,name, enabled=False, selected=False, value=None):
        if name=="accept":
            return {'value':'Accept','clickable':enabled,'onclickjson':{"type":"change_vote","vote":"accept"}}
        if name=="reject":
            return {'value':'Reject','clickable':enabled,'onclickjson':{"type":"change_vote","vote":"reject"}}
        if name=="fail":
            return {'value':'Fail','clickable':enabled,'onclickjson':{"type":"mission_card","vote":"fail"}}
        if name=="success":
            return {'value':'Success','clickable':enabled,'onclickjson':{"type":"mission_card","vote":"success"}}
        if name=="name":
            if selected:
                return {'value':value,'clickable':enabled,'onclickjson':{"type":"change_team","name":value,"select":not selected},'style':{'background-color': '#f7de6d'}}
            else:
                return {'value':value,'clickable':enabled,'onclickjson':{"type":"change_team","name":value,"select":not selected},'style':{'background-color': 'transparent'}}
        if name=="empty":
            return {'value':'','clickable':False}

    def team_select_setup(self):
        output={}
        for player in self.players:
            updates={}
            for player2 in self.players:
                if player2 in self.team:
                    if player==self.king:
                        updates[player2+'TeamBox']=self.get_card("name",True,True,player2)
                    else:
                        updates[player2+'TeamBox']=self.get_card("name",False,True,player2)
                else:
                    if player==self.king and len(self.team)<self.missions[self.current_mission][0]:
                        updates[player2+'TeamBox']=self.get_card("name",True,False,player2)
                    else:
                        updates[player2+'TeamBox']=self.get_card("name",False,False,player2)
                updates[player2+'TeamBox']['style'].update({'width':str(int(100.0/len(self.players)))+'%','display': 'inline-block', 'float':'left'})
            if player==self.king and len(self.team)==self.missions[self.current_mission][0]:
                updates['submitButton']={'clickable':True,'onclickjson':'submit_team'}
            #print(updates)
            output[player]={'updates':updates}
        return output
    
    def team_select_player_select(self,player_id,select=True):
        output={}
        updates={}
        other_updates={}
        #print(select)
        updates[player_id+'TeamBox']=self.get_card("name",True,select,player_id)
        other_updates[player_id+'TeamBox']=self.get_card("name",False,select,player_id)
        if select:
            self.team.append(player_id)
            if(len(self.team)==self.missions[self.current_mission][0]):
                for player in self.players:
                    if player not in self.team:
                        updates[player+'TeamBox']=self.get_card("name",False,False,player) #name_spot(player)
                updates['submitButton']={'clickable':True,'onclickjson':{"type":"submit_team"}}
        else:
            self.team.remove(player_id)
            if(len(self.team)==self.missions[self.current_mission][0]-1):
                for player in self.players:
                    if player not in self.team:
                        updates[player+'TeamBox']=self.get_card("name",True,False,player)#name_button(player,True)
                updates['submitButton']={'clickable':False}
        output[self.king]={'updates':updates}
        for player in self.people:
            if player!=self.king:
                output[player]={'updates':other_updates}
        #print(output)
        return output
    
    def get_role_info(self,role):
        if role=="Spectator":
            return "Click on a player if you want to know their role"
        elif role=='merlin':
            out="The minions of Mordred are "
            for person in self.roles['minions']+self.roles['morgana']+self.roles['oberon']+self.roles['assassin']:
                out+=person+", "
            out=out[:-2]
            return out
        elif role=='percival':
            out="Merlin is one of "
            for person in self.roles['merlin']+self.roles['morgana']:
                out+=person+", "
            out=out[:-2]
            return out
        elif role=='minions' or role=='morgana' or role=='mordred' or role=='assassin':
            out="Your teamates are "
            for person in self.roles['minions']+self.roles['morgana']+self.roles['mordred']+self.roles['assassin']:
                out+=person+", "
            out=out[:-2]
            return out
        else:
            return "You have no info. Learn what you can from the votes and missions"
    def team_select_cleanup(self):
        output={}
        updates={}
        self.waiting=[]
        self.phase="team_voting"
        for player in self.players:
            self.waiting.append(player)
            updates[player+'TeamBox']={'clickable':False}
        output[self.king]={'updates':updates}

        self.toRun.append(self.team_voting_setup)
        self.args.append({})
        return output
        
    def team_voting_setup(self):
        output={}
        for player in self.players:
            updates={}
            if player in self.waiting:
                updates['acceptCard']=self.get_card('accept',True)
                updates['rejectCard']=self.get_card('reject',True)
                updates['submitButton']={'clickable':False}
            else:
                updates['acceptCard']=self.get_card('accept',False)
                updates['rejectCard']=self.get_card('reject',False)
                updates['submitButton']={'clickable':False}
            output[player]={'updates':updates}

        return output

    def team_voting_cleanup(self):
        output={}
        updates={}
        updates['acceptCard']=self.get_card('empty')
        updates['rejectCard']=self.get_card('empty')
        updates['submitButton']={'clickable':False}
        
        accepts=0
        rejects=0
        box_style={'display':'inline-block','width':'5%','text-align':'center'}
        self.history[self.turn]={'king':self.king,'team':self.team.copy(),'votes':self.votes.copy()}

        updates['history'+str(self.turn)+'King']={'id': 'history'+str(self.turn)+'King', 'type':'card','value':self.history[self.turn]['king'],'clickable':False,'visible':True,'style':box_style.copy()}
        updates['history'+str(self.turn)+'missionResult']={'id': 'history'+str(self.turn)+'missionResult', 'type':'card','value':"",'clickable':False,'visible':True,'style':box_style.copy()}
        rowObjects=['history'+str(self.turn)+'King','history'+str(self.turn)+'missionResult']
        for player in self.players:
            if self.history[self.turn]['votes'][player]=="accept":
                updates['history'+player+str(self.turn)+'Box']={'id': 'history'+player+str(self.turn)+'Box', 'type':'card','value':"Y",'clickable':False,'visible':True,'style':box_style.copy()}
            else:
                updates['history'+player+str(self.turn)+'Box']={'id': 'history'+player+str(self.turn)+'Box', 'type':'card','value':"N",'clickable':False,'visible':True,'style':box_style.copy()}
            if player in self.history[self.turn]['team']:
                updates['history'+player+str(self.turn)+'Box']['style'].update({'background-color':'#f7de6d'})
            rowObjects.append('history'+player+str(self.turn)+'Box')
        updates['history'+str(self.turn)+'Row']={'id':'history'+str(self.turn)+'Row','type':'container','objects':rowObjects,'style':{'display':'block'}}
        print(updates)
        newRowList=['historyHeaderRow']
        turns=list(self.history.keys())
        turns.sort(reverse=True)
        for turn in turns:
            newRowList.append('history'+str(turn)+'Row')
        updates['historyTable']={'objects':newRowList}
        #rows.append('history'+str(row)+'Row')
        
        for vote in self.votes.values():
            if(vote=="accept"):
                accepts+=1
            elif(vote=="reject"):
                rejects+=1
        if accepts>rejects:
            self.toRun.append(self.do_mission_setup)
            self.args.append({})
            
            updates['messageBox']={'value':"Mission Approved"}
            self.waiting=[]
            for player in self.team:
                self.waiting.append(player)
            self.phase="on_mission"
            #print("Mission Approved")
        else:
            self.turn+=1
            self.vote_count+=1
            updates['voteNumber']={'value':'Vote: '+str(self.vote_count+1)+'/5'}
            self.team=[]
            if self.vote_count>4:
                updates['messageBox']={'value':'You just lost, you fools'}
                self.toRun.append(self.victory)
                self.args.append({})
            else:
                self.toRun.append(self.team_select_setup)
                self.args.append({})
            updates['messageBox']={'value':"Mission Rejected"}
            self.king=self.players[(self.players.index(self.king)+1)%len(self.players)]
            self.waiting=[self.king]
            self.phase="team_select"
            #print("Mission Rejected")
        for p in self.people:
            output[p]={'updates':updates,'turn':self.turn}
        return output

    def team_voting_change_vote(self,player,vote):
        updates={}
        updates['submitButton']={'clickable':True,'onclickjson':{"type":"submit_vote","vote":vote}}
        if vote=="accept":
            updates['acceptCard']=self.get_card('accept',False,True)
            updates['rejectCard']=self.get_card('reject',True)
        elif vote=="reject":
            updates['rejectCard']=self.get_card('reject',False,True)
            updates['acceptCard']=self.get_card('accept',True)
        return {player:{'updates':updates}}

    def team_voting_submit_vote(self,player,vote):
        self.votes[player]=vote
        self.waiting.remove(player)
        output={}
        updates={}
        updates['acceptCard']=self.get_card("accept",False)
        updates['rejectCard']=self.get_card("reject",False)
        updates['submitButton']={'clickable':False}
        if len(self.waiting)==0:
            self.toRun.append(self.team_voting_cleanup)
            self.args.append({})
        else:
            print(self.waiting)
        output[player]={'updates':updates}
        return output

    def do_mission_setup(self):
        output={}
        for player in self.players:
            updates={}
            if player in self.team:
                if player not in self.roles["good"] and player not in self.roles["merlin"] and player not in self.roles["percival"]:
                    updates['rejectCard']=self.get_card("fail",True)
                    updates['acceptCard']=self.get_card("success",True)
                else:
                    updates['rejectCard']=self.get_card("fail",False)
                    updates['acceptCard']=self.get_card("success",False,True)
                    updates['submitButton']={'clickable':True,'onclickjson':{'type':'submit_mission','vote':'success'}}
            output[player]={'updates':updates}
        return output

    def merge_outputs(self,a,b,player=None):
        templist=self.people
        if player:
            templist=[player]
        #print(a)
        #print(b)
        for player_id in templist:
            if player_id in b:
                if player_id not in a:
                    a[player_id]=b[player_id]
                else:
                    if 'turn' in b[player_id]:
                        a[player_id]['turn']=b[player_id]['turn']
                    for key in b[player_id]['updates']:
                        if key in a[player_id]['updates']:
                            for key2 in b[player_id]['updates'][key]:
                                if key2=="style" and key2 in a[player_id]['updates'][key]:
                                    a[player_id]['updates'][key]['style'].update(b[player_id]['updates'][key]['style'])
                                else:
                                    a[player_id]['updates'][key][key2]=b[player_id]['updates'][key][key2]
                        else:
                            a[player_id]['updates'][key]=b[player_id]['updates'][key]
        #print(a)
        
        return a


    def do_mission_pick_card(self,player,vote):
        updates={}
        updates['submitButton']={'clickable':True,'onclickjson':{"type":"submit_mission","vote":vote}}
        if vote=="success":
            updates['acceptCard']=self.get_card('success',False)
            updates['rejectCard']=self.get_card('fail',True)
        elif vote=="fail":
            updates['rejectCard']=self.get_card('fail',False)
            updates['acceptCard']=self.get_card('success',True)
        return {player:{'updates':updates}}

    #THIS IS FOR MISSSSSSSIONSSSSS!!!!!
    def do_mission_submit(self,player,vote):
        if vote=="success":
            self.succeeds+=1
        else:
            self.fails+=1
        self.waiting.remove(player)
        output={}
        updates={}
        updates['acceptCard']=self.get_card("success")
        updates['rejectCard']=self.get_card("fail")
        updates['submitButton']={'clickable':False}
        if len(self.waiting)==0:
            self.toRun.append(self.do_mission_cleanup)
            self.args.append({})
        else:
            pass
            #print(self.waiting)
        output[player]={'updates':updates,'turn':self.turn}
        return output

    def do_mission_cleanup(self):
        output={}
        self.history[self.turn]['fail']=self.fails
        self.history[self.turn]['succeeds']=self.succeeds
        updates={}
        updates['history'+str(self.turn)+'missionResult']={'value':str(self.history[self.turn]['fail'])}
        if self.fails<self.missions[self.current_mission][1]:
            self.mission_history.append("success")
            updates['messageBox']={'value':"Mission Succeeded"}
            updates['mission'+str(self.current_mission)+'Number']={'style':{'background-color':'#72d8f7'}}
            #print("Mission Passed")
        else:
            self.mission_history.append("fail")
            updates['messageBox']={'value':'Mission failed with ' + str(self.fails) + 'played'}
            updates['mission'+str(self.current_mission)+'Number']={'style':{'background-color':'#dd0000'}}
            #print("Mission Failed")
        self.current_mission+=1
        yes=0
        no=0
        for mission in self.mission_history:
            if mission=="success":
                yes+=1
            if mission=="fail":
                no+=1
        if yes>2 and len(self.roles['assassin'])>0:
                self.toRun.append(self.setup_assassin_guess)
                self.args.append({})
                updates['messageBox']={'value':'Assassin Guess'}
                self.phase="assassin"
                self.waiting=[]
                for player in self.roles['assassin']:
                    self.waiting.append(player)
                #print("Assassin Phase!")
        elif no>2 or self.current_mission>=len(self.missions):
                self.toRun.append(self.victory)
                self.args.append({})
                #print("Evil wins!")
        else:
            self.toRun.append(self.team_select_setup)
            self.args.append({})
            self.phase="team_select"
            self.team=[]
            self.votes={}
            self.vote_count=0
            self.turn+=1
            self.king=self.players[(self.players.index(self.king)+1)%len(self.players)]
            self.fails=0
            self.succeeds=0
            self.waiting=[self.king]
        updates['voteNumber']={'value':'Vote: '+str(self.vote_count+1)+"/5"}
        for person in self.people:
            output[person]={'updates':updates,'turn':self.turn}
        return output

    def setup_assassin_guess(self):
        output={}
        updates={}
        #print("here assassin")
        for player in self.roles['assassin']:
            #print(player)
            for player2 in self.players:
                #print(self.roles['merlin']+self.roles['percival']+self.roles['good'])
                if player2 in self.roles['merlin']+self.roles['percival']+self.roles['good']:
                    updates[player2+'TeamBox']={'value':player2,'clickable':True,'onclickjson':{'type':'assassin_guess','name':player2}}
                    #updates[player2+'onTeamBox']={'value':'_______','clickable':False}
                else:
                    updates[player2+'TeamBox']={'value':'','clickable':False,'visible':False}
                    #updates[player2+'offTeamBox']={'value':'','clickable':False,'visible':False}
                updates['messageBox']={'value':'Guess which player was Merlin'}
            output[player]={'updates':updates}
        #print(output)
        return output

    def make_assassin_guess(self,player):
        if player in self.roles['merlin']:
            self.vote_count+=10
        self.toRun.append(self.victory)
        self.args.append({})
        return {}

    def victory(self):
        self.phase="done"
        output={}
        winner="good"
        if self.vote_count>4:
            winner="evil"
        passes=0
        for mission in self.mission_history:
            if mission=="succeed":
                passes+=1
        if passes<3:
            winner="evil"
        for player in self.players:
            output[player]={'updates':{'messageBox':{'value': winner+' won!'}}}
        #print(output)
        return output

    def setup_lobby(self):
        updates={}
        peopleList=[]
        for person in self.people:
            updates[person+'TeamBox']={'id':person+'TeamBox', 'type': 'card', 'value': person, 'clickable':True,'visible':True,'style':{'width':str(int(100.0/len(self.people)))+'%','display': 'inline-block', 'float':'left','margin': 'auto auto','text-align':'center'}}
            if person in self.players:
                updates[person+'TeamBox']['style'].update({'background-color':'#00ff00'})
                updates[person+'TeamBox']['onclickjson']={'type':'lobby_remove','name':person}
            else:
                updates[person+'TeamBox']['style'].update({'background-color':'transparent'})
                updates[person+'TeamBox']['onclickjson']={'type':'lobby_add','name':person}
            peopleList.append(person+'TeamBox')
        rolesList=[]
        for role in ['merlin','morgana','assassin','mordred','oberon','percival']:
            updates[role+'Box']={'id':role+'Box', 'type': 'card', 'value': role, 'clickable':True,'visible':True,'style':{'width':str(int(100.0/6))+'%','display': 'inline-block', 'float':'left','margin': 'auto auto','text-align':'center'}}
            if eval('self.'+role):
                updates[role+'Box']['style'].update({'background-color':'#00ff00'})
                updates[role+'Box']['onclickjson']={'type':'role_remove','name':role}
            else:
                updates[role+'Box']['style'].update({'background-color':'transparent'})
                updates[role+'Box']['onclickjson']={'type':'role_add','name':role}
            rolesList.append(role+'Box')
        updates['playersBox']={'id':'playersBox', 'type':'container','objects': peopleList,'visible':True,'style':{'width':'100%','display': 'block', 'float':'left'}}
        updates['rolesBox']={'id':'rolesBox', 'type':'container','objects': rolesList,'visible':True,'style':{'width':'100%','display': 'block', 'float':'left'}}
        updates['startButton']={'id':'startButton','type':'card','clickable':True,'visible':True,'value':'Start Game!','onclickjson':{'type':'game_start'}}
        updates[0]={'objects':['playersBox','rolesBox','startButton']}
        return updates

    def handle_lobby(self, arg, value):
        output={}
        updates={}

        if arg=="lobby_add":
            #print("add")
            if value not in self.players:
                self.players.append(value)
            updates[value+'TeamBox']={'style':{'background-color':'#00ff00'},'onclickjson':{'type':'lobby_remove','name':value}}
        if arg=="lobby_remove":
            #print("remove")
            if value in self.players:
                self.players.remove(value)
            updates[value+'TeamBox']={'style':{'background-color':'transparent'},'onclickjson':{'type':'lobby_add','name':value}}
        if arg=="role_add":
            if value=='merlin':
                self.merlin=True
            elif value=='mordred':
                self.mordred=True
            elif value=='assassin':
                self.assassin=True
            elif value=='morgana':
                self.morgana=True
            elif value=='oberon':
                self.oberon=True
            elif value=='percival':
                self.percival=True
            updates[value+'Box']={'style':{'background-color':'#00ff00'},'onclickjson':{'type':'role_remove','name':value}}
        if arg=="role_remove":
            if value=='merlin':
                self.merlin=False
            elif value=='mordred':
                self.mordred=False
            elif value=='assassin':
                self.assassin=False
            elif value=='morgana':
                self.morgana=False
            elif value=='oberon':
                self.oberon=False
            elif value=='percival':
                self.percival=False
            updates[value+'Box']={'style':{'background-color':'transparent'},'onclickjson':{'type':'role_add','name':value}}
        for person in self.people:
            output[person]={'updates':updates}
        #print(output)
        #print(self.players,self.people)
        return output

    def setup_board(self,player_id):
        updates={}
        role="Spectator"
        for key in self.roles:
            if player_id in self.roles[key]:
                role=key
        updates['myRole']={'id':'myRole', 'type':'card','value': "You are "+role_descriptors[role]['name'],'style':{'display':'block'},'clickable':False}
        updates['myGoal']={'id':'myGoal', 'type':'card','value': role_descriptors[role]['goal'],'style':{'display':'block'},'clickable':False}
        updates['myInfo']={'id':'myInfo', 'type':'card','value': self.get_role_info(role),'style':{'display':'block'},'clickable':False}
        missionBoxes=['voteBox']
        for i in range(0,len(self.missions)):
            updates['mission'+str(i)+'Box']={'id':'mission'+str(i)+'Box','type':'container','objects':['mission'+str(i)+'Number'],'style':{'display':'inline-block','width':'15%'}}
            updates['mission'+str(i)+'Number']={'id':'mission'+str(i)+'Number','type':'card','value':str(self.missions[i][0]),'clickable':False}
            missionBoxes.append('mission'+str(i)+'Box')
            if i<self.current_mission:
                if self.mission_history[i]=="success":
                    updates['mission'+str(i)+'Number']['style']={'background-color':'#72d8f7'}
                elif self.mission_history[i]=="fail":
                    updates['mission'+str(i)+'Number']['style']={'background-color':'#dd0000'}
        updates['missionDisplay']={'id':'missionDisplay','type':'container','objects':missionBoxes,'style':{'width':'100%'}}
        teamRowList=[]
        otherRowList=[]
        for player in self.players:
            updates[player+'TeamBox']={'id':player_id+'TeamBox', 'type': 'card', 'value': player, 'clickable':False,'visible':True,'style':{'width':str(int(100.0/len(self.players)))+'%','display': 'inline-block', 'float':'left','margin': 'auto auto','text-align':'center'}}
            teamRowList.append(player+'TeamBox')
        updates['myRoleBox']={'id':'myRoleBox','type':'container','objects':['myRole','myGoal','myInfo']}
        updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "", 'clickable':False, 'visible':True}
        updates['teamsBox']={'id':'teamsBox', 'type':'container','objects': ['onTeamRow'],'visible':True,'style':{'width':'100%','display': 'block', 'float':'left'}}
        updates['onTeamRow']={'id':'onTeamRow', 'type':'container','objects': teamRowList,'visible':True,'style':{'width':'100%','display': 'block', 'float':'top'}}
        #updates['offTeamRow']={'id':'offTeamRow', 'type':'container','objects': otherRowList,'visible':True,'style':{'width':'100%','display': 'block', 'float':'top'}}
        updates['centerBox']={'id':'centerBox', 'type':'container','objects':['gameDisplay','mainRow'],'visible':True,'style':{'width':'100%','display': 'block', 'float':'left'}}
        updates['gameDisplay']={'id':'gameDisplay', 'type':'container','objects':['myRoleBox','messageBox','missionDisplay'],'visible':True}
        updates['voteBox']={'id':'voteBox','type':'container','objects':['voteNumber'],'style':{'display':'inline-block','width':'15%'}}
        updates['voteNumber']={'id':'voteNumber','type':'card', 'value':"Vote: "+str(self.vote_count+1)+"/5",'style':{'display': 'block'},'clickable':False,'visible':True}
        updates['mainRow']={'id': 'mainRow', 'type':'container','objects':['voteRow','submitRow'],'visible':True}
        updates['voteRow']={'id': 'voteRow', 'type':'container','objects':['acceptCard','rejectCard'],'visible':True}
        updates['acceptCard']={'id': 'acceptCard', 'type':'card','value':"",'clickable':False,'visible':True}
        updates['rejectCard']={'id': 'rejectCard', 'type':'card','value':"",'clickable':False,'visible':True}
        updates['submitRow']={'id':'submitRow','type':'container','objects':['submitButton']}
        updates['submitButton']={'id':'submitButton','type':'card','value':"submit",'clickable':False,'visible':True}
        turns=list(self.history.keys())
        print(turns)
        turns.sort(reverse=True)


        box_style={'display':'inline-block','width':'5%','text-align':'center'}
        updates['kingBox']={'id': 'kingBox', 'type':'card','value':"King",'clickable':False,'visible':True,'style':box_style.copy()}
        updates['failBox']={'id': 'kingBox', 'type':'card','value':"Fails",'clickable':False,'visible':True,'style':box_style.copy()}
        header=['kingBox','failBox']
        for player in self.players:
            header.append(player+'NameBox')
            updates[player+'NameBox']={'id': player+'NameBox', 'type':'card','value':player,'clickable':False,'visible':True,'style':box_style.copy()}
        rows=['historyHeaderRow']
        updates['historyHeaderRow']={'id':'historyHeaderRow','type':'container','objects':header}
        for row in turns:
            print(row)
            updates['history'+str(row)+'King']={'id': 'history'+str(row)+'King', 'type':'card','value':self.history[row]['king'],'clickable':False,'visible':True,'style':box_style.copy()}
            if 'fail' in self.history[row]:
                updates['history'+str(row)+'missionResult']={'id': 'history'+str(row)+'missionResult', 'type':'card','value':str(self.history[row]['fail']),'clickable':False,'visible':True,'style':box_style}
            else:
                updates['history'+str(row)+'missionResult']={'id': 'history'+str(row)+'missionResult', 'type':'card','value':"",'clickable':False,'visible':True,'style':box_style.copy()}
            rowObjects=['history'+str(row)+'King','history'+str(row)+'missionResult']
            for player in self.players:
                if self.history[row]['votes'][player]=="accept":
                    updates['history'+player+str(row)+'Box']={'id': 'history'+player+str(row)+'Box', 'type':'card','value':"Y",'clickable':False,'visible':True,'style':box_style.copy()}
                else:
                    updates['history'+player+str(row)+'Box']={'id': 'history'+player+str(row)+'Box', 'type':'card','value':"N",'clickable':False,'visible':True,'style':box_style.copy()}
                if player in self.history[row]['team']:
                    updates['history'+player+str(row)+'Box']['style'].update({'background-color':'#f7de6d'})
                rowObjects.append('history'+player+str(row)+'Box')
            updates['history'+str(row)+'Row']={'id':'history'+str(row)+'Row','type':'container','objects':rowObjects,'style':{'display':'block'}}
            rows.append('history'+str(row)+'Row')
        
        updates['historyTable']={'id':'historyTable','type':'container','objects':rows,'style':{'width':'100%'}}
        updates[0]={'objects':['teamsBox','centerBox','historyTable']}
        return updates
    
    def setup_game(self):
        output={}
        for person in self.people:
            updates=self.setup_board(person)
            output[person]={'updates':updates}
        return output
    
    
def update_with_move(path, move, data, player_id):
    print(move,data,player_id)
    state=load_state(path)
    game=state['board']
    updates={}
    if 'type' in data and data['type']=='get_player_info':
        grole="Specator"
        for role in game.roles:
            if data['name'] in game.roles[role]:
                grole=role
        updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "That person is "+role_descriptors[grole], 'clickable':False, 'visible':True}
        return {player_id:{'updates':updates}}
    if move < state['turn']:
        updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "That turn has passed", 'clickable':False, 'visible':True}
        return {player_id:{'updates':updates}}
    if player_id not in game.waiting:
        updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "It's not your turn", 'clickable':False, 'visible':True}
        return {player_id:{'updates':updates}}
    if 'type' not in data:
        updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "No move specified", 'clickable':False, 'visible':True}
        return {player_id:{'updates':updates}}
    output={}
    if data['type']=="change_team":
        if 'name' not in data or 'select' not in data:
            updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "Not enough data for move", 'clickable':False, 'visible':True}
            return {player_id:{'updates':updates}}
        game.toRun.append(game.team_select_player_select)
        game.args.append({'player_id':data['name'],'select':data['select']})
    elif data['type']=="submit_team":
        game.toRun.append(game.team_select_cleanup)
        game.args.append({})
    elif data['type']=="change_vote":
        game.toRun.append(game.team_voting_change_vote)
        game.args.append({'player':player_id,'vote':data['vote']})
    elif data['type']=="submit_vote":
        game.toRun.append(game.team_voting_submit_vote)
        game.args.append({'player':player_id,'vote':data['vote']})
    elif data['type']=="mission_card":
        game.toRun.append(game.do_mission_pick_card)
        game.args.append({'player':player_id,'vote':data['vote']})
    elif data['type']=="submit_mission":
        game.toRun.append(game.do_mission_submit)
        game.args.append({'player':player_id,'vote':data['vote']})
    elif data['type']=="assassin_guess":
        game.toRun.append(game.make_assassin_guess)
        game.args.append({'player':data['name']})
    elif data['type']=="lobby_remove" or data['type']=="lobby_add" or data['type']=="role_remove" or data['type']=="role_add":
        #print("here1")
        game.toRun.append(game.handle_lobby)
        game.args.append({'arg':data['type'],'value':data['name']})
    elif data['type']=="game_start":
        game.toRun.append(game.start)
        game.args.append({})
    else:
        updates['messageBox']={'id': 'messageBox', 'type': 'card', 'value': "Not a valid move right now", 'clickable':False, 'visible':True}
        return {player_id:{'updates':updates}}
    while len(game.toRun)>0:
        func=game.toRun.pop()
        arg={}
        if len(game.args)>0:
            arg=game.args.pop()
        output=game.merge_outputs(output,func(**arg))
        save_state(path,state)
    print(game.waiting)
    #print(output)
    return output

def get_state_updates(path, start_move, end_move, player_id):
    state=load_state(path)
    game=state['board']
    #print(game.phase)
    updates={}
    if game.phase=="lobby":
        updates=game.setup_lobby()
        return {'updates':updates}
    if start_move==-1:
        updates=game.setup_board(player_id)
    move=end_move
    if end_move==-1:
        move=state['turn']
    output={player_id:{'updates':updates}}
    if game.phase=="team_select":
        game.merge_outputs(output,game.team_select_setup(),player_id)
    if game.phase=="team_voting":
        game.merge_outputs(output,game.team_voting_setup(),player_id)
    if game.phase=="on_mission":
        game.merge_outputs(output,game.do_mission_setup(),player_id)
    if game.phase=="assassin":
        game.merge_outputs(output,game.setup_assassin_guess(),player_id)
    if game.phase=="done":
        game.merge_outputs(output,game.victory(),player_id)
    print(game.history)
    #print(game.waiting,game.phase,game.king,player_id)
    #print(output[player_id]['updates'])
    return output[player_id]
