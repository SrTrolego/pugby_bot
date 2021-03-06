from random import choice
import sys, os
 
class SquadDic():
    def __init__(self):
        self._chars = (
            "A","B","C","D","E","F","G","H","I","J","K","L","M","N",
            "O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b",
            "c","d","e","f","g","h","i","j","k","l","m","n","o","p",
            "q","r","s","t","u","v","w","x","y","z","0","1","2","3",
            "4","5","6","7","8","9"
            )
        # synchronized lists
        self.chats_ids = []
        self.messages_ids = []
        # synchronized lists
        self.jobs = {}
        self.groups_ids = []
        self.group_message_ids = {} # [(chat_id,message_id)]
        # "CodeNameDuoOrSquad":[["user1",uid1,False],["user2",uid,False]]
        self.duos = {}
        self.squads = {}
        # "user":[cid,d_ab12]]
        self.users = {}
        
    def clear_all(self):
        self.chats_ids = []
        self.messages_ids = []
        self.groups_ids = []
        self.group_message_ids = {} 
        self.duos = {}
        self.squads = {}
        self.users = {}
        
    def add_group_message_id(self,cid,mid,group):
        key = str(mid)+"_"+str(cid)
        if self.group_message_ids.get(key) is None:
            self.group_message_ids[key] = group
            
    def get_group_message_id(self,cid,mid):
        key = str(mid)+"_"+str(cid)
        if self.group_message_ids.get(key) is not None:
                return self.group_message_ids[key]
        else:
            return False
            
    def to_register_job(self,cid,mid,job,group):
        self.jobs[str(cid)+"_"+str(mid)] = (job,group)
        
    def delete_group_job(self,cid,mid):
        try:
            key = str(cid)+"_"+str(mid)
            g = None
            if self.jobs.get(key) is not None:
                job,group = self.jobs[key]
                index = self.groups_ids.index(group)
                job.schedule_removal()
                del self.jobs[key]
                del self.groups_ids[index]
                if self.group_message_ids.get(key):
                    del self.group_message_ids[key]
                if self.duos.get(group):
                    g = self.duos[group]
                    del self.duos[group]
                elif self.squads.get(group):
                    g = self.squads[group]
                    del self.squads[group]
            if g is not None:
                for user in g:
                    if self.users.get(user[0]) is not None:
                        if self.users[user[0]][1] == g:
                            del self.users[user[0]]
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
                        
    def repalace_job_id(self, cid_new, mid_new, cid_old, mid_old):
        key_new = str(cid_new)+"_"+str(mid_new)
        key_old = str(cid_old)+"_"+str(mid_old)
        if self.jobs.get(key_old) is not None:
            self.jobs[key_new] = self.jobs[key_old]
            del self.jobs[key_old]
    
    def expire_group(self):
        if self.duos.get(self.groups_ids[0]):
            del self.duos[self.groups_ids[0]]
            del self.groups_ids[0]
        elif self.squads.get(self.groups_ids[0]):
            del self.squads[self.groups_ids[0]]
            del self.groups_ids[0]
            
    def add_message_id(self, message_id, chat_id):
        self.messages_ids.append(message_id)
        self.chats_ids.append(chat_id)
        
    def expire_message(self):
        if self.messages_ids:
            message_id = self.messages_ids[0]
            chat_id = self.chats_ids[0]
            del self.messages_ids[0]
            del self.chats_ids[0]
            return message_id,chat_id
        else:
            return False
     
    def create_duo(self,user,cid):
        code_name = self._generate_code_name("d_")
        if code_name is None:
            return "try_again"
        self.groups_ids.append(code_name)
        self.duos[code_name] = [[None,None,False],[None,None,False]]
        if self.users.get(user) is None:
            self.users[user] = [cid,code_name]
        else:
            self.users[user][1] = code_name
        return code_name
        
    def create_squad(self,user,cid):
        code_name = self._generate_code_name("s_")
        if code_name is None:
            return "try_again"
        self.groups_ids.append(code_name)
        self.squads[code_name] = [[None,None,False],[None,None,False],
            [None,None,False],[None,None,False]]
        if self.users.get(user) is None:
            self.users[user] = [cid,code_name]
        else:
            self.users[user][1] = code_name
        return code_name
        
    def join(self,user,uid,group,to_join=False):
        c = self._check_user(user,group)
        if self.duos.get(group) is not None:
            groups = self.duos
        elif self.squads.get(group) is not None:
            groups = self.squads
        else:
            return 0
        if c == 0: # 0 There is no group
            return False
        elif c == 1: # 1 User in group
            for u in groups[group]:
                if u[0] == user:
                    u[2] = to_join
                    return 1
        elif c == 2: # User without group
            for u in groups[group]:
                if u[0] is None:
                    u[0] = user
                    u[1] = uid
                    u[2] = to_join
                    return 2
            return 4 # Team full
            
    def leave(self,user,group):
        c = self._check_user(user,group)
        if self.duos.get(group) is not None:
            groups = self.duos
        elif self.squads.get(group) is not None:
            groups = self.squads
        else:
            return 0
        if c == 0: # 0 There is no group
            return 0
        elif c == 1: # User in group
            for u in groups[group]:
                if u[0] == user:
                    u[0] = None
                    u[1] = None
                    u[2] = False
                    return 1
        else:# User without group
            return 2
        
    def dissolve_group(self,group):
        g = None
        if self.duos.get(group) is not None:
            g = self.duos[group]
            del self.duos[group]
        elif self.squads.get(group) is not None:
            g = self.duos[group]
            del self.duos[group]
        if g is not None:
            for user in g:
                if self.users.get(user[0]) is not None:
                    if self.users[user[0]][1] == g:
                        del self.users[user[0]]
                        return True
        return False
                
    def get_group_users(self,group):
        if self.duos.get(group) is not None:
            return self.duos[group]
        elif self.squads.get(group) is not None:
            return self.squads[group]
        else:
            return None
                
    def get_group(self,user):
        if self.users.get(user) is not None:
            return self.users[user][1]
        else:
            return None
            
    def _generate_code_name(self,start):
        # Create the code name of a duo or squad
        # For duo "d_xxxx"
        # For squad "s_xxxx"
        if start == "d_":
            dic = self.duos
        else:
            start = "s_"
            dic = self.squads
        for i in range(100):
            name = start
            for i2 in range(4):
                name += choice(self._chars)
            if dic.get(name) is None:
                return name
        return None
    
    def _check_user(self,user,group):
        # check if a user is in a duo or squad
        # 0 There is no group
        # 1 user in group
        # 2 user without group 
        if self.duos.get(group) is not None:
            groups = self.duos
        elif self.squads.get(group) is not None:
            groups = self.squads
        else:
            return 0
        for u in groups[group]:
            if u is not None:
                if u[0] == user:
                    return 1
        return 2
            
            

