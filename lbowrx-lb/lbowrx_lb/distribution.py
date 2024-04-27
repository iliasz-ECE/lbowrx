import threading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from lbowrx_lb.config.dynamic import DynamicConfig

class ServerInfo():
    def __init__(self, server_id):
        server_info = DynamicConfig.get_servers_object().get_server_info(server_id)
        self.name = server_info.name
        self.ip = server_info.ip
        self.port = server_info.port
        self.priority = server_info.priority
        self.initial_response = False
        self.init_state_tag = None
        self.responding = False
        self.cpu = None
        self.sdrs = {}
    
    def update_cur(self,server_dict):
        self.responding = server_dict["responding"]
        if self.responding:
            self.cpu = server_dict["latest_avg_cpu_usage"]
            return self.init_state_tag != server_dict["init_state_tag"]
        else:
            return False

class SdrInfo():
    def __init__(self):
        self.name = None
        self.type = None 
        self.priority = None
        self.usage = None
        self.failed = None
        self.disabled = None
        self.has_users = None
        self.cur_profile_id = None
        self.num_of_connections = None
        self.profiles = {}

    def update_init(self,sdr_dict):
        self.name = sdr_dict["name"]
        self.type = sdr_dict["type"]
        
        if "enabled" in sdr_dict:
            self.disabled = not sdr_dict["enabled"]
        else:
            self.disabled = False
        if "priority" in sdr_dict:
            self.priority = sdr_dict["priority"]
        else:
            self.priority = 100
        if "usage" in sdr_dict:
            self.usage = sdr_dict["usage"]
        else:
            self.usage = "exclusive"
            
    def update_cur(self,sdr_dict):
        self.failed = sdr_dict["failed"]
        self.has_users = sdr_dict["has_users"]
        self.num_of_connections = sdr_dict["number_of_connections"]
        self.cur_profile_id = sdr_dict["current_profile"]["profile_id"]

class ProfileInfo():
    def __init__(self, center_freq, sample_rate):
        self.center_freq = center_freq 
        self.sample_rate = sample_rate

class Distribution():
    servers_state_db = {}
    state_lock = threading.Lock()
    
    
    @classmethod
    def create_init_state(cls, loglevel=None):
    
        if loglevel:
            logger.setLevel(loglevel)
    
        cls.state_lock.acquire()
        cls.servers_state_db = {}
        
        for server_id in DynamicConfig.get_servers().keys():
            server_info = ServerInfo(server_id)
            cls.servers_state_db.update({server_id: server_info})
            
        cls.state_lock.release()
        logger.debug("Created initial state")
    
    @classmethod
    def add_init_state(cls, init_dict):
        cls.state_lock.acquire()
        
        for server_id, server_dict in init_dict.items():
            server_info = ServerInfo(server_id)
            server_info.initial_response = server_dict["initial_response"] 
            
            if server_dict["initial_response"]:
                del server_dict["initial_response"]
                
                server_info.init_state_tag = server_dict["init_state_tag"]
                del  server_dict["init_state_tag"]
            
                for sdr_id, sdr_dict in server_dict.items():
                    sdr_info = SdrInfo()
                    sdr_info.update_init(sdr_dict)
                    server_info.sdrs.update({sdr_id: sdr_info})
                    
                    for profile_id, profile_dict in sdr_dict["profiles"].items():
                        profile_info = ProfileInfo(profile_dict["center_freq"], profile_dict["samp_rate"])
                        sdr_info.profiles.update({profile_id: profile_info})

            cls.servers_state_db.update({server_id: server_info})
            
        cls.state_lock.release()
        logger.debug("Added initial state")
        
    @classmethod
    def update_cur_state(cls, cur_dict):
        cls.state_lock.acquire()
        
        ret = []
        for server_id, server_dict in cur_dict.items():
            if cls.servers_state_db[server_id].update_cur(server_dict):
                logger.debug("change in server: %s init state", cls.servers_state_db[server_id].name)
                ret.append(server_id)
                continue
            
            if server_dict["responding"]:
                del server_dict["latest_avg_cpu_usage"]
                del server_dict["responding"]
                del server_dict["init_state_tag"]
                
                for sdr_id, sdr_dict in server_dict.items():
                    cls.servers_state_db[server_id].sdrs[sdr_id].update_cur(sdr_dict)
        
        cls.state_lock.release()
        if not ret:
            logger.debug("Updated current state")
        # ret is a list of server id when init state is needed
        return ret

    
    @classmethod
    def get_servers(cls):
        all_servers_dict = {}
        for server_id, server in cls.servers_state_db.items():
            server_dict = {}
            server_dict.update({"name": server.name})
            server_dict.update({"ip": server.ip})
            server_dict.update({"port": server.port})
            server_dict.update({"priority": server.priority})
            server_dict.update({"responding": server.responding})
            if server.responding:
                server_dict.update({"cpu": server.cpu})
                num_of_active_sdrs = 0
                total_connections = 0
                
                for sdr in server.sdrs.values():
                    if (not sdr.disabled) and (not sdr.failed):
                        num_of_active_sdrs += 1
                        total_connections += sdr.num_of_connections
                        
                server_dict.update({"active_sdrs": num_of_active_sdrs}) 
                server_dict.update({"connections": total_connections})
        
            all_servers_dict.update({server_id: server_dict})
        
        return all_servers_dict
                
    @classmethod
    def add_server(cls, server_id):
        server_info = ServerInfo(server_id)
        cls.servers_state_db.update({server_id: server_info}) 
                
    @classmethod
    def delete_server(cls, server_id):
        del cls.servers_state_db[server_id]

    @classmethod
    def modify_server(cls, server_id):
        del cls.servers_state_db[server_id]
        server_info = ServerInfo(server_id)
        cls.servers_state_db.update({server_id: server_info}) 


    @classmethod
    def get_sdrs(cls):
        all_sdrs_dict = {}
        for server in cls.servers_state_db.values():
            if server.responding:
                for sdr_id, sdr in server.sdrs.items():
                    sdr_dict = {}
                    sdr_dict.update({"name": sdr.name})
                    sdr_dict.update({"server": server.name})
                    sdr_dict.update({"type":sdr.type})
                    sdr_dict.update({"priority": sdr.priority})
                    sdr_dict.update({"profiles_num": len(sdr.profiles)})
                    sdr_dict.update({"available": (not sdr.failed) and (not sdr.disabled)})
                    sdr_dict.update({"connections": sdr.num_of_connections})
                    all_sdrs_dict.update({sdr_id: sdr_dict})
            
        return all_sdrs_dict
        
    @classmethod
    def get_server_info(cls,server_id):
        return cls.servers_state_db[server_id]
        
    @classmethod
    def check_profiles_match(cls,checked_profile,selected_profile):
        start_freq = checked_profile.center_freq - checked_profile.sample_rate/2
        end_freq = checked_profile.center_freq + checked_profile.sample_rate/2
        
        return start_freq <= selected_profile.start_freq and end_freq >= selected_profile.end_freq
        
    @staticmethod
    def score_sort(candidate_tuple):
        # negation for reversing sort order.
        return (candidate_tuple[3], -candidate_tuple[4])    
        
    @classmethod
    def print_match_list(cls,match_list):
        servers = cls.servers_state_db
        for x in match_list:
            server_id = x[0]
            server_name = servers[server_id].name
            sdr_id = x[1]
            sdr_name = servers[server_id].sdrs[sdr_id].name
            profile_id = x[2]
            profile_freq = servers[server_id].sdrs[sdr_id].profiles[profile_id].center_freq
            logger.debug((server_name,sdr_name,profile_freq,x[3],x[4]))
        
    @classmethod
    def decision_algorithm(cls, selected_profile_id, failed_sdrs_list):
        cls.state_lock.acquire()
        
        selected_profile_info = DynamicConfig.get_profiles_object().get_profile_info(selected_profile_id)
        
        match_list = []
        score = 0
        for server_id, server_info in cls.servers_state_db.items():
            server_available = server_info.responding
            
            if server_info.priority > 0:
                server_score = server_info.priority
            else:
                server_available = False
            
            if server_available:
                if server_info.cpu > 0.5 and server_info.cpu <= 0.8:
                    server_score -= 20
                if server_info.cpu > 0.8:
                    server_available = False
                
            if server_available:
                for sdr_id, sdr_info in server_info.sdrs.items():
                    sdr_available = (not sdr_info.failed) and (not sdr_info.disabled) and (not sdr_id in failed_sdrs_list) 
                    sdr_score = sdr_info.priority
                    
                    if sdr_available:
                        if sdr_info.has_users:
                            if cls.check_profiles_match(sdr_info.profiles[sdr_info.cur_profile_id],selected_profile_info):
                                sdr_score += 10
                                profile_id = sdr_info.cur_profile_id
                                score = server_score + sdr_score
                                sample_rate = sdr_info.profiles[sdr_info.cur_profile_id].sample_rate
                                match_list.append((server_id,sdr_id,profile_id,score,sample_rate))
                            else:
                                sdr_available = False
                                continue
                    
                        else:
                            for profile_id, profile_info in sdr_info.profiles.items():
                                if cls.check_profiles_match(profile_info, selected_profile_info):
                                    score = server_score + sdr_score
                                    sample_rate = profile_info.sample_rate
                                    match_list.append((server_id,sdr_id,profile_id,score,sample_rate))
        cls.state_lock.release()

        match_list.sort(reverse = True, key=cls.score_sort)
        cls.print_match_list(match_list)

        best_match = max(match_list, key=cls.score_sort, default=None)
        if best_match: 
            return (best_match[0],best_match[1],best_match[2])
        else:
            logger.debug("No Decision - No Sdr match")
            return None
            
