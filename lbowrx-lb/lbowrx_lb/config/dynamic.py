from uuid import uuid4   
import json

from lbowrx_lb.config.core import CoreConfig

class ServersConfig():
    def __init__(self):
        self.servers = {}
        
    def get_server_info(self,server_id):
        if server_id in self.servers:
            return self.servers[server_id]
        else:
            return None
        
    def add_server(self,server_id,server_info_dict):
        new_server_info = ServerInfo(server_info_dict["name"],server_info_dict["ip"],server_info_dict["port"],server_info_dict["priority"])
        self.servers.update({server_id: new_server_info})
        
class ServerInfo():
    def __init__(self,name,ip,port,priority):
        self.name = name
        self.ip = ip
        self.port = port
        self.priority = priority
        
class ProfilesConfig():
    def __init__(self):
        self.profiles = {}

    def get_profile_info(self,profile_id):
        if profile_id in self.profiles:
            return self.profiles[profile_id]
        else:
            return None
        
    def add_profile(self,profile_id,profile_info_dict):
        new_profile_info = ProfileInfo(profile_info_dict["name"],profile_info_dict["start_freq"],profile_info_dict["end_freq"])
        self.profiles.update({profile_id: new_profile_info})
    
    
    def to_id_list(self):
        profiles_list = []
        for profile_id in self.profiles.keys():
            profiles_list.append(profile_id)
        return profiles_list    
    
    
    def to_id_name_list(self):
        profiles_list = []
        for profile_id, profile_info in self.profiles.items():
            profiles_list.append({"id": profile_id, "name": profile_info.name})
        return profiles_list

class ProfileInfo():
    def __init__(self,name,start_freq,end_freq):
        self.name = name
        self.start_freq = start_freq
        self.end_freq = end_freq

class DynamicConfig():
    sharedConfig = None

    def __init__(self):
        self.servers = ServersConfig()
        self.profiles = ProfilesConfig()
        self.receiver_details = {}
        try:
            with open(DynamicConfig._getSettingsFile(), "r") as f:
                for k, v in json.load(f).items():
                    if k == "servers":
                        for server_id, server_info_dict in v.items():
                            self.servers.add_server(server_id,server_info_dict)
                    elif k == "profiles":
                        for profile_id, profile_info_dict in v.items():
                            self.profiles.add_profile(profile_id, profile_info_dict)
                    elif k == "receiver_details":
                        for key, value in v.items():
                            if key == "receiver_gps":
                                self.receiver_details.update({"receiver_gps": {"lat": value["lat"], "lon": value["lon"]}})
                            else:
                                self.receiver_details.update({key: value})
                        
            DynamicConfig.sharedConfig = self

        except FileNotFoundError:
            pass
          
            
    @classmethod
    def get(cls):
        if cls.sharedConfig is None:
            cls.sharedConfig = cls()
        return cls.sharedConfig
    
    
    @classmethod
    def get_servers(cls):
        return cls.get().servers.servers
    
    @classmethod
    def get_servers_object(cls):
        return cls.get().servers
    
    @classmethod
    def add_server(cls, server_id, server_info):
        config = cls.get()
        servers_config = config.servers.servers
        servers_config[server_id] = server_info
        config.store()
    
    @classmethod
    def modify_server(cls, server_id, server_info):
        config = cls.get()
        servers_config = config.servers.servers
        servers_config[server_id] = server_info
        config.store()
    
    @classmethod
    def delete_server(cls, server_id):
        config = cls.get()
        servers_config = config.servers.servers
        del servers_config[server_id]
        config.store()
    
    
    @classmethod
    def get_profiles(cls):
        return cls.get().profiles.profiles
    
    @classmethod
    def get_profiles_object(cls):
        return cls.get().profiles
   
     
    @classmethod
    def get_profiles_id_list(cls):
        return cls.get().profiles.to_id_list()
    
    @classmethod
    def get_profiles_id_name_list(cls):
        return cls.get().profiles.to_id_name_list()    
    
    @classmethod
    def add_profile(cls, profile_id, profile_info):
        config = cls.get()
        profiles_config = config.profiles.profiles
        profiles_config[profile_id] = profile_info
        config.store()
    
    @classmethod
    def modify_profile(cls, profile_id, profile_info):
        config = cls.get()
        profiles_config = config.profiles.profiles
        profiles_config[profile_id] = profile_info
        config.store()
    
    @classmethod
    def delete_profile(cls, profile_id):
        config = cls.get()
        profiles_config = config.profiles.profiles
        del profiles_config[profile_id]
        config.store()
    
    
    @classmethod
    def get_receiver_details(cls):
        return cls.get().receiver_details
    
    @classmethod
    def modify_receiver_details(cls, receiver_details):
        config = cls.get()
        config.receiver_details = receiver_details
        config.store()
    
    
    @staticmethod
    def _getSettingsFile():
        coreConfig = CoreConfig()
        return "{data_directory}/lb-settings.json".format(data_directory=coreConfig.get_data_directory())
   
    def to_dict(self):
        config_dict = {}
        
        servers_dict = {}
        for server_id, server_info in self.servers.servers.items():
            servers_dict.update({server_id: server_info.__dict__})
        config_dict.update({"servers": servers_dict})
        
        profiles_dict = {}
        for profile_id, profile_info in self.profiles.profiles.items():
            profiles_dict.update({profile_id: profile_info.__dict__})
        config_dict.update({"profiles": profiles_dict})
        
        config_dict.update({"receiver_details": self.receiver_details})
        
        return config_dict
   
    def store(self):
        # don't write directly to file to avoid corruption on exceptions
        jsonContent = json.dumps(self.to_dict(), indent=4)
        with open(DynamicConfig._getSettingsFile(), "w") as file:
            file.write(jsonContent)
