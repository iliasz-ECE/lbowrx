import threading

import logging

logger = logging.getLogger(__name__)


class CpuUsageThread(threading.Thread):
    sharedInstance = None
    creationLock = threading.Lock()
    
    cpu1 = 0.0
    cpu2 = 0.0
    cpu3 = 0.0
    latest_cpu_usage = 0.0
    latest_cpu_usage_lock = threading.Lock()

    
    # keep last 3 measurements and average them
    @classmethod
    def setCpuUsage(cls,last_cpu):
        cls.cpu3 = cls.cpu2
        cls.cpu2 = cls.cpu1
        cls.cpu1 = last_cpu
        latest_avg_cpu = round((cls.cpu1+cls.cpu2+cls.cpu3)/3,3)
        cls.latest_cpu_usage_lock.acquire()
        cls.latest_cpu_usage = latest_avg_cpu
        cls.latest_cpu_usage_lock.release()
    
    @staticmethod
    def getLatestCpu():
        CpuUsageThread.latest_cpu_usage_lock.acquire()
        cpu = CpuUsageThread.latest_cpu_usage 
        CpuUsageThread.latest_cpu_usage_lock.release()
        return cpu
    
    
    @staticmethod
    def getSharedInstance():
        with CpuUsageThread.creationLock:
            if CpuUsageThread.sharedInstance is None:
                CpuUsageThread.sharedInstance = CpuUsageThread()
        return CpuUsageThread.sharedInstance

    def __init__(self):
        self.clients = []
        self.doRun = True
        self.last_worktime = 0
        self.last_idletime = 0
        self.endEvent = threading.Event()
        self.startLock = threading.Lock()
        super().__init__()

    def run(self):
        logger.debug("cpu usage thread starting up")
        while self.doRun:
            try:
                cpu_usage = self.get_cpu_usage()
            except:
                cpu_usage = 0
            for c in self.clients:
                c.write_cpu_usage(cpu_usage)
            
            CpuUsageThread.setCpuUsage(cpu_usage)
            self.endEvent.wait(timeout=3)
        logger.debug("cpu usage thread shut down")

    def get_cpu_usage(self):
        try:
            f = open("/proc/stat", "r")
        except:
            return 0
        line = ""
        while not "cpu " in line:
            line = f.readline()
        f.close()
        spl = line.split(" ")
        worktime = int(spl[2]) + int(spl[3]) + int(spl[4])
        idletime = int(spl[5])
        dworktime = worktime - self.last_worktime
        didletime = idletime - self.last_idletime
        rate = float(dworktime) / (didletime + dworktime)
        self.last_worktime = worktime
        self.last_idletime = idletime
        if self.last_worktime == 0:
            return 0
        return rate

    def add_client(self, c):
        self.clients.append(c)
        with self.startLock:
            if not self.is_alive():
                self.start()

    def remove_client(self, c):
        try:
            self.clients.remove(c)
        except ValueError:
            pass
        if not self.clients:
            self.shutdown()

    def shutdown(self):
        with CpuUsageThread.creationLock:
            CpuUsageThread.sharedInstance = None
        
        CpuUsageThread.latest_cpu_usage = 0.0
        CpuUsageThread.cpu1 = 0.0
        CpuUsageThread.cpu2 = 0.0
        CpuUsageThread.cpu3 = 0.0
        self.doRun = False
        self.endEvent.set()
