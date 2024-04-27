import threading
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from lbowrx_lb.config.dynamic import DynamicConfig
from lbowrx_lb.distribution import Distribution

class ReceiveServersStateThread(threading.Thread):
    shared_instance = None

    def __init__(self, loglevel=None):
        self.loglevel = loglevel
        if loglevel:
            logger.setLevel(loglevel)
        
        self.doRun = True
        self.wakeEvent = threading.Event()
        self.wakeEvent.clear()
        self.workedEvent = threading.Event()
        self.workedEvent.clear()
        
        super().__init__()
        ReceiveServersStateThread.shared_instance = self
    
    @classmethod
    def wake_and_wait_until_thread_works(cls):
        if cls.shared_instance is None:
            cls.shared_instance = cls()
        
        cls.shared_instance.wakeEvent.set()
        cls.shared_instance.workedEvent.wait()
        cls.shared_instance.workedEvent.clear()
        
    def run(self):
        logger.info("Receive State Thread is running")
        
        Distribution.create_init_state(self.loglevel)
        self.receive_cur_servers_state()
        
        while self.doRun:
            self.wakeEvent.wait(30)
            
            if self.doRun == False:
                break
                  
            self.receive_cur_servers_state()
            if self.wakeEvent.is_set():
                self.wakeEvent.clear()
                self.workedEvent.set()
                    
        
    def shutdown(self):
        self.doRun = False
        self.wakeEvent.set()
        
    def receive_init_servers_state(self, servers_target_list):
        target_servers_dict = {}

        servers = DynamicConfig.get_servers()
        
        for server_id in servers_target_list:
            server_info = servers[server_id]
            
            ip = server_info.ip
            port = server_info.port
            
            server_dict = {}
    
            url = "http://" + ip + ':' + str(port) + "/initstate.json"
            
            try:
                r = requests.get(url, timeout=(2,2))
                server_dict = r.json()
                server_dict.update({"initial_response": True})
            except:
                server_dict.update({"initial_response": False})
                
            target_servers_dict.update({server_id: server_dict})
            
        Distribution.add_init_state(target_servers_dict)
                
    def receive_cur_servers_state(self):
        all_servers_dict = {}
        servers = DynamicConfig.get_servers()
        for server_id, server_info in servers.items():
            ip = server_info.ip
            port = server_info.port
            
            server_dict = {}
    
            url = "http://" + ip + ':' + str(port) + "/curstate.json"
            
            try:
                r = requests.get(url, timeout=(1,1))
                server_dict = r.json()
                server_dict.update({"responding": True})
            except:
                server_dict.update({"responding": False})
                logger.debug(server_info.ip + " is not responding")
                    
            all_servers_dict.update({server_id: server_dict})
            
        ret = Distribution.update_cur_state(all_servers_dict)
        
        # If there is no initial state receive it.
        if ret:
            self.receive_init_servers_state(ret)
            self.receive_cur_servers_state()
