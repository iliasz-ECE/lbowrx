import json
from uuid import uuid4

from owrx.controllers import Controller
from owrx.sdr import SdrService
from owrx.config import Config
from owrx.connection import OpenWebRxReceiverClient
from owrx.source import SdrClientClass
from owrx.cpu import CpuUsageThread



class StateController(Controller):
    init_state_tag = str(uuid4())
    
    @classmethod
    def update_state_tag(cls):
        cls.init_state_tag = str(uuid4())

# Sends all sdrs and profiles of the server. Sends once at beggining.
class InitialStateController(StateController):
    def indexAction(self):
        sdrs_dict = {}
        for sdrid,sdr in Config.get()["sdrs"].items():
            sdr_full_dict = {}
            sdr_full_dict.update({"name": sdr["name"]})
            if "type" in sdr.keys():
                sdr_full_dict.update({"type": sdr["type"]})
            if "device" in sdr.keys():
                sdr_full_dict.update({"device": sdr["device"]}) 
            if "enabled" in sdr.keys():
                sdr_full_dict.update({"enabled": sdr["enabled"]})
            if "priority" in sdr.keys():
                sdr_full_dict.update({"priority": sdr["priority"]})
            else:
                print("\nError: You need to specify priority in settings of {}\n".format(sdr["name"]))
                
            sdr_profiles_dict = {}
            for profileid,profile in sdr["profiles"].items():
                profile_dict = {}
                for (key,value) in profile.items():
                    profile_dict.update({key:value})
                sdr_profiles_dict.update({profileid: profile_dict})
                
            sdr_full_dict.update({"profiles": sdr_profiles_dict})
            
            sdrs_dict.update({sdrid: sdr_full_dict})
            
        
        sdrs_dict.update({"init_state_tag": self.init_state_tag})
        
        json_state = json.dumps(sdrs_dict)
        self.send_response(json_state, content_type="application/json")
   
# Sends periodically and on demand the part of state that changes.     
class CurrentStateController(StateController):
    def indexAction(self):   
        current_state = {}
        current_state.update({"latest_avg_cpu_usage": CpuUsageThread.getLatestCpu()})
        sources = SdrService.getAllSources()
        
        for sdrid,source in sources.items():
            sdr_info_dict = {}
            sdr_name = (Config.get()["sdrs"][sources[sdrid].id]["name"])
            sdr_info_dict.update({"sdr_name": sdr_name})
            
            sdr_info_dict.update({"has_users": source.hasClients(SdrClientClass.USER)})
            connections = []
            clients = source.getClients()
            for client in clients:
                if isinstance(client, OpenWebRxReceiverClient):
                    connections.append(client)        
            sdr_info_dict.update({"number_of_connections": len(connections)})
            
            profiles = source.getProfiles()
            current_profile = profiles[source.getProfileId()]
            
            sdr_info_dict.update({"current_profile": {"profile_id": source.getProfileId()}})
            sdr_info_dict["current_profile"].update(current_profile.__dict__())
            
            sdr_info_dict.update({"failed": source.isFailed()})
            
            current_state.update({sdrid: sdr_info_dict})
        
        
        current_state.update({"init_state_tag": self.init_state_tag})
        
        json_state = json.dumps(current_state)
        self.send_response(json_state, content_type="application/json")
