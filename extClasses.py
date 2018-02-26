import subprocess, threading
from time import sleep
from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal

class pinger(QObject):
    
    stateChangedSignal = pyqtSignal(str, bool)
    def __init__(self, address, timeout = 1, messages = None):
        """
        address - plain text (ip or domain name, ex. www.address.com)
        messages - queue for getting information (optional)
        
        """
        super(pinger, self).__init__()
        self.__address = address
        self.__messages = messages
        self.state = False
        self.enabled = True
        self.__timeout = timeout
        
        
        
        
    def __ping(self):
        """
        Returns True if host responds to a ping request
        """
        import platform
        ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
        ping_string = "ping " + ping_str + " " + self.__address
        if platform.system().lower() != "windows":
            result = subprocess.call(ping_string, stdout = subprocess.DEVNULL, shell = True) == 0
        else:
            result = False
            p = subprocess.Popen(ping_string, shell = True, stdout = subprocess.PIPE)
            lines = []
            for i in p.stdout:
                lines.append(str(i, 'cp866'))
            for i in lines:
                if i[:(9 + len(self.__address))] == 'Ответ от ' + self.__address:
                    result = True
        return result    
        
    
    
    def __mainloop(self):
        while self.enabled:
            state = self.__ping()
            if self.state != state:
                self.__stateChanged(state)
            sleep(self.__timeout)
    
    def __stateChanged(self, state):
        if self.__messages != None: self.__messages.put([self.__address, state])
        self.state = state
        self.stateChangedSignal.emit(self.__address, state)
        
    def start(self, delay = 0):
        sleep(delay)
        self.t = threading.Thread(target = self.__mainloop, args = ())
        self.t.daemon = True
        self.t.start()
        
    def stop(self):
        if self.state: self.__messages.put([self.__address, False])
        self.enabled = False

    
    




