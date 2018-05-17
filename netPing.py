# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from datetime import datetime
from time import sleep

import configparser
import csv
import os
import serial
import tkinter.ttk as ttk
import threading, queue, tkinter
from tkinter import messagebox
try: import ui.tk_NetPing_support as tk_NetPing_support
except: import tk_NetPing_support
from ui.extClasses import pinger
import ui.tk_NetPing as npMain
import ui.tk_settingsForm as tk_settingsForm
try: import tk_settingsForm_support
except: import ui.tk_settingsForm_support as tk_settingsForm_support

"""
раз в секунду принимаем от нетпинга в ASCII знак и две цифры температуры
раз в секунду отправляем 11
22 - перезагрузить модем (200 раз - модем перезагрузится)
44 - перезагрузка всего (или арены)
66 - отключить приём команд кроме 77
77 - включить приём команд
33 - доп реле 1 перезагрузить
55 - доп реле 2 перезагрузить
перезагрузка при превышении температуры происходит по команде с компа(44)
"""

class comLoop:
    
    def __init__(self):
        super(comLoop, self).__init__()
        self.com = None
        self.speed = None
        self.needToRebootModem = False
        self.autoChangeSpeedCounter = 3
        self.autoSpeed = None
        self.restarting = False
        self.comSendCommandQueue = queue.Queue()
        self.comEnabled = False
        self.state = {'opened':False, 'temp':'', 'sleeping':0, 'speed':self.speed}
        self.queue = queue.Queue()
        self.t1enabled = True
        self.t1 = threading.Thread(target = self.__queueHandler, args = (self.queue,))
        self.t1.start()
    
    def start(self, delay = 0):
        if not self.needToRebootModem: self.comSendCommandQueue.put('1')
        else: self.comSendCommandQueue.put('2')
        self.comEnabled = True
        self.t = threading.Thread(target = self.__comLoop, args = (delay, ))
        self.t.start()
        return(0)
    
    def settingsChanged(self, com, speed, auto = True):
        print('111')
        try:
            if self.ser.port != com or self.speed != speed or auto != self.autoSpeed:
                print('changing')
                if self.stop() == 0:
                    self.ser.port = com
                    self.com = com
                    self.ser.baudrate = speed
                    self.speed = speed
                    if auto: 
                        self.autoSpeed = True
                        self.autoChangeSpeedCounter = 3
                        self.restart(2)
                    else: 
                        self.autoSpeed = False
                        self.restart(2)
            else: 
                if not self.comEnabled: self.start(0)
        except:
            print('starting new com')
            self.com = com
            self.speed = speed
            self.autoSpeed = auto
            if auto: 
                self.autoSpeed = True
                self.autoChangeSpeedCounter = 3
                self.start(0)
            else: 
                self.autoSpeed = False
                self.start(0)
    
    def restart(self, delay = 10):
        if not self.restarting:
            self.restarting = True
            print('restarting COM, delay = ' + str(delay))
            if self.stop() == 0: 
                self.state = {'opened':False, 'temp':'', 'sleeping':delay, 'speed':self.speed}
                print('com restart, delay = ' + str(delay))
                self.start(delay)
    
    def autoChangeSpeed(self): 
        print('autoChange counter = ' + str(self.autoChangeSpeedCounter))
        if self.autoChangeSpeedCounter > 0 and self.autoSpeed and self.comEnabled: 
            print(self.speed)
            self.autoChangeSpeedCounter -= 1
            if self.speed == 1200: 
                self.speed = 9600 
            else: 
                self.speed = 1200
            print('speed changed,now ' + str(self.speed))
            self.restart(2)
            return True
        elif self.autoSpeed == False and self.comEnabled:
            print('possibly wrong speed, auto disabled')
            self.restart(2)
            return False
        elif self.comEnabled: 
            print('autospeed not successful, restart com')
            self.autoChangeSpeedCounter = 3
            self.restart(10)
            return False
        else:
            print("stopping com")
    
    def stop(self):
        self.comEnabled = False
        try:
            while self.t.is_alive():
                print('thread still alive')
                sleep(.5)
        except: print('thread finished')
        finally:
            try:
                if self.ser.is_open(): self.ser.close()
            except: pass
        print('com stopped')
        return 0
    
    def sendCommand(self, command):
        print(self.com + ' command sent: ' + command)
        self.comSendCommandQueue.put(command)
    
    def __comLoop(self, delay):
        self.queue.put(['message', 'comLoop started'])
        com = self.com
        speed = self.speed
        auto = self.autoSpeed
        while delay > 0 and self.comEnabled:
            self.queue.put(['sleep', delay])
            delay -= 1
            sleep(1)
        self.queue.put(['sleep', 0])
        self.restarting = False
        comState = False
        comSendCommand = '1'
        rebootModem = False
        try: 
            self.queue.put(['message', 'try open ' + com + ' at speed ' + str(speed)])
            counter = 0
            badCounter = 3
            temp = ''
            self.ser = serial.Serial(com)
            self.ser.baudrate = speed
            self.ser.timeout = 1
            while self.comEnabled:
                rebootModem = self.needToRebootModem
                if self.ser.readline() == b'': 
                    counter += 1
                    self.queue.put(['message', 'read empty'])
                    if counter > 5: 
                        if comState:
                            self.queue.put(['state', [False, None]])
                            comState = False
                            self.ser.close()
                        if self.comEnabled: self.queue.put(['command', 'autoChangeSpeed'])
                else:
                    if self.comEnabled: ttemp = self.ser.readline().decode('ascii')
                    sleep(.1)
                    if self.comEnabled:
                        self.ser.write(bytes(comSendCommand, 'ascii'))
                        self.queue.put(['message', ttemp + ', write ' + comSendCommand])
                        if ttemp != temp:
                            temp = ttemp
                            self.queue.put(['temp', temp])
                        if len(ttemp) == 3: 
                            badCounter = 3
                            if auto: 
                                self.queue.put(['command', 'DisableAutoSpeed'])
                                auto = False
                            if not comState:
                                comState = True
                                self.queue.put(['state', [True, speed]])
                            if temp != ttemp:
                                temp = ttemp
                                self.queue.put(['temp', temp])
                        elif len(ttemp) > 0 and badCounter > 0:
                            badCounter -= 1
                            sleep(.5)
                            if self.comEnabled: self.ser.reset_input_buffer()
                            self.queue.put(['message', 'something wrong, read = ' + ttemp + ' remains attempts ' + str(badCounter)])
                        else: 
                            self.queue.put(['message', 'something wrong, read = ' + ttemp])
                            self.ser.close()
                            if self.comEnabled: self.queue.put(['command',  'autoChangeSpeed'])
                    if comSendCommand != '1' and comSendCommand != '2':
                        if self.comEnabled: self.ser.reset_output_buffer()
                        counter += 1
                        if counter >= 2 and self.comEnabled: ##Количество повторений отправки команд, можно попробовать уменьшить для увеличения скорости отклика, но есть риск непрохождения команды
                            try:
                                comSendCommand = self.comSendCommandQueue.get_nowait()
                                if comSendCommand == '1': rebootModem = False
                                elif comSendCommand == '2': rebootModem = True
                                counter = 0
                            except:
                                if not rebootModem: comSendCommand = '1'
                                else: comSendCommand = '2'
                    else: 
                        counter = 0
                        try:
                            comSendCommand = self.comSendCommandQueue.get_nowait()
                            if comSendCommand == '1': rebootModem = False
                            elif comSendCommand == '2': rebootModem = True
                        except:
                            if not rebootModem: comSendCommand = '1'
                            else: comSendCommand = '2'
            self.ser.close()
            if comState: 
                self.queue.put(['state', [False, None]])
                comState = False
        except Exception as e: 
            if str(e) == "Port is already open.": 
                self.ser.close()
                if self.comEnabled: self.restart(1)
            else:
                self.queue.put(['state', [False, None]])
                comState = False
                self.queue.put(['message', str(e)])
                self.queue.put(['command',  'autoChangeSpeed'])
        
    def __queueHandler(self, q_input):
        while self.t1enabled:
            try:
                msg = q_input.get_nowait()
                if msg[0] == 'message': print(msg[1])
                elif msg[0] == 'state': 
                    self.state['opened'] = msg[1][0]
                    if self.state['opened']: self.state['speed'] = msg[1][1]
                elif msg[0] == 'temp': self.state['temp'] = msg[1]
                elif msg[0] == 'command': 
                    if msg[1] == 'autoChangeSpeed': self.autoChangeSpeed()
                    elif msg[1] == 'DisableAutoSpeed': self.autoSpeed = False
                elif msg[0] == 'sleep': self.state['sleeping'] = msg[1]
                else: pass
            except:
                sleep(.3)

class MainWindow():
    def __init__(self, parent=None):
        self.start_gui()
        self.statusMessage = tkinter.StringVar()
        self.comState = tkinter.StringVar()
        self.ip1State = tkinter.StringVar()
        self.ip2State = tkinter.StringVar()
        self.ip1 = ""
        self.ip2 = ""
        self.w.TLabel1.configure(textvariable = self.statusMessage)
        self.w.send_command.entryconfig('Restart COM', command = self.__restartCom)
        self.w.send_command.entryconfig('Enable commands (7)', command = self.on_enableCommandsAction_triggered)
        self.w.send_command.entryconfig('Disable commands (6)', command = self.on_disableCommandsAction_triggered)
        self.w.send_command.entryconfig('Reboot all (4)', command = self.on_restartAllAction_triggered)
        self.w.send_command.entryconfig('Reboot modem', command = self.on_restartModemAction_toggled)
        self.w.other_commands.entryconfig('3', command = self.on_sendCommand3_triggered)
        self.w.other_commands.entryconfig('5', command = self.on_sendCommand5_triggered)
        self.w.more.entryconfig('Setup', command = self.on_settingsAction_triggered)
        self.w.more.entryconfig('New log', command = self.on_createNewLogAction_triggered)
        self.w.more.entryconfig('Clear current log', command = self.on_clearLogAction_triggered)
        self.messages = queue.Queue()
        self.watchdogEnabled = True
        self.c = comLoop()
        self.readConfig()
        try: 
            with open('tmp') as tmp: self.logWrite('Abnormal shutdown', 1, tmp.read())
        except: pass
        self.t1 = threading.Thread(target = self.watchdog, args = ())
        self.t1.daemon = True
        self.t1.start()
        self.t2 = threading.Thread(target = self.__com_watcher, args = ()) ## Будет работать только без Qt
        self.t2.start()
        self.logWrite('Startup', 0)
        root.protocol("WM_DELETE_WINDOW", self.closeEvent)
        root.mainloop()
    
    def start_gui(self):
        global val, w, root
        root = tkinter.Tk()
        tk_NetPing_support.set_Tk_var()
        self.w = npMain.New_Toplevel (root)
        icon = tkinter.Image("photo", file = './ui/icons/notification.png')
        root.wm_iconphoto('True', icon)
        root.geometry("300x450-20+50")
        tk_NetPing_support.init(root, self.w)

    def readConfig(self):
        self.config = configparser.ConfigParser(allow_no_value = True)
        try:
            self.w.comState.pack_forget()
        except:
            pass
        try:
            self.w.ip1state.pack_forget()
        except:
            pass
        try:
            self.w.ip2state.pack_forget()
        except:
            pass
        try:
            self.config.read('settings.ini')
            print('config read success, ' + self.config['comtest']['port'])
        except:
            print('write new config')
            self.config['iptest'] = {}
            self.config['iptest']['ip1'] = ''
            self.config['iptest']['ip2'] = ''
            self.config['comtest'] = {}
            self.config['comtest']['enabled'] = 'False'
            self.config['comtest']['port'] = 'COM9'
            self.config['comtest']['speed'] = '1200'
            self.config['comtest']['autoSpeed'] = 'True'
            self.config['comtest']['maxtemp'] = '70'
            self.config['logsettings'] = {}
            self.config['logsettings']['maxlogsize'] = '1048576'
            self.config['logsettings']['onsysup'] = 'True'
            self.config['logsettings']['onsysdown'] = 'True'
            self.config['logsettings']['ip1'] = 'False'
            self.config['logsettings']['ip2'] = 'False'
            self.config['logsettings']['com'] = 'False'
            self.config['logsettings']['tempchange'] = 'False'
            self.config['logsettings']['flags'] = '110000'
            self.config['modemsettings'] = {}
            self.config['modemsettings']['ip1'] = 'False'
            self.config['modemsettings']['ip2'] = 'False'
            configfile = open('settings.ini', 'w')
            self.config.write(configfile)
            configfile.close()
        self.logRead() # читаем лог соответственно настройкам отображения
        self.needToRebootModem1 = False
        self.needToRebootModem2 = False
        self.needToRebootModem3 = False
        if self.config.getboolean('comtest', 'enabled'):
            self.w.comState = ttk.Label(self.w.frame1)
            self.w.comState.configure(textvariable = self.comState)
            self.w.comState.pack(side = 'bottom', fill = 'x')
            self.w.menubar.entryconfig('Send command', state = 'normal')
            if not self.c.state['opened']: self.comStateChanged('Starting ' + self.config['comtest']['port'])
            else: self.tempChanged(self.c.state['temp'])
            print('changing settings of comLoop')
            self.c.settingsChanged(self.config['comtest']['port'], self.config['comtest']['speed'], self.config.getboolean('comtest', 'autoSpeed'))
        else:
            self.w.menubar.entryconfig('Send command', state = 'disabled')
            try: 
                self.c.stop()
            except: pass
        if self.config['iptest']['ip1'] != '':
            self.ip1 = self.config['iptest']['ip1']
            self.ip1State.set(self.ip1 + ' does not response')
            self.w.ip1state = ttk.Label(self.w.frame1)
            self.w.ip1state.configure(textvariable = self.ip1State)
            self.w.ip1state.pack(side = 'top', fill = 'x')
            self.ip1 = self.config['iptest']['ip1']
            self.p1 = pinger(self.ip1, 5, self.messages)
            self.ipStateChanged( self.ip1, False)
            self.p1.start()
        else: 
            try: self.p1.stop()
            except: pass
        if self.config['iptest']['ip2'] != '':
            self.ip2 = self.config['iptest']['ip2']
            self.ip2State.set(self.ip2 + ' does not response')
            self.w.ip2state = ttk.Label(self.w.frame1)
            self.w.ip2state.configure(textvariable = self.ip2State)
            self.w.ip2state.pack(side = 'top', fill = 'x')
            self.ip2 = self.config['iptest']['ip2']
            self.p2 = pinger(self.ip2, 5, self.messages)
            self.ipStateChanged( self.ip2, False)
            self.p2.start()
        else: 
            try: self.p2.stop()
            except: pass
        
    def ipStateChanged(self, ip, state):
        try:
            if ip == self.ip1: 
                logcat = 2
                if self.config.getboolean('modemsettings', 'ip1'):
                    if not state and self.config.getboolean('modemsettings', 'ip1'): self.needToRebootModem1 = True
                    if state: self.needToRebootModem1 = False
            if ip == self.ip2:
                logcat = 3
                if self.config.getboolean('modemsettings', 'ip2'):
                    if not state and self.config.getboolean('modemsettings', 'ip2'): self.needToRebootModem2 = True
                    if state: self.needToRebootModem2 = False
        except: pass
        if self.config.getboolean('comtest', 'enabled') == True: self.c.needToRebootModem = bool(self.needToRebootModem1 + self.needToRebootModem2 + self.needToRebootModem3)
        if state: text = ip + ' avialible'
        else: text = ip + ' unavialible'
        if ip == self.ip1:
           self.ip1State.set(text)
        if ip == self.ip2:
            self.ip2State.set(text)
        self.logWrite(text, logcat)
    
    def logWrite(self, text, category, time = None):
        self.statusMessage.set(text)
        if time == None: dt = datetime.now().strftime('%H:%M:%S %d/%m/%y')
        else: dt = time
        with open('log.txt',  'a', newline='') as logfile:
            logwriter = csv.writer(logfile, dialect='unix')
            logwriter.writerow([category, dt, text])
            if self.config['logsettings']['flags'][category] == '1': 
                self.w.Scrolledtext1.insert(tkinter.END, (dt + ' ' + text + '\n'))
                self.w.Scrolledtext1.see(tkinter.END)
    
    def logRead(self):
        try: #create empty log if there is no file
            a = open('log.txt', 'x')
            a.write('')
            a.close()
        except: 
            if os.path.getsize('log.txt') > int(self.config['logsettings']['maxlogsize']):
                self.on_createNewLogAction_triggered()
                self.logWrite('Log is too big, started new one',  1)
        with open('log.txt', newline = '') as logfile: #read log
            self.w.Scrolledtext1.delete(1.0, tkinter.END)
            try:
                logreader = csv.reader(logfile, dialect = "unix")
            except:
                self.on_createNewLogAction_triggered()
                self.logWrite('Log is damaged, started new one',  1)
                logreader = csv.reader(logfile, dialect = "unix")
            for row in logreader:
                if self.config['logsettings']['flags'][int(row[0])] == '1':
                    self.w.Scrolledtext1.insert(tkinter.END, (row[1] + ' ' + row[2] + '\n'))
                    self.w.Scrolledtext1.see(tkinter.END)
    
    def watchdog(self):
        while self.watchdogEnabled:
            tmpfile = open('tmp', 'w')
            tmpfile.write(datetime.now().strftime('%H:%M:%S %d/%m/%y'))
            tmpfile.close()
            self.statusMessage.set(datetime.now().strftime('%H:%M %d/%m') + ' controlling...')
            try: 
                if self.c.needToRebootModem: self.statusMessage.set(datetime.now().strftime('%H:%M %d/%m') + ' waiting for modem reboot...')
            except: pass
            sleep(15)
            
    def comStateChanged(self, text):
        self.comState.set(text)
        
    def tempChanged(self, temp):
        self.comState.set(self.c.com + ' is active, t = ' + temp)
        self.statusMessage.set(datetime.now().strftime('%H:%M:%S %d/%m') + ' t = ' + temp)
        if len(temp) == 3: 
            self.logWrite(('t = ' + str(temp)), 5)
            if int(temp[1:]) >= int(self.config['comtest']['maxtemp']): 
                self.logWrite('OVERHEATING!!!', 4)
                self.c.sendCommand('4')
        
    def comStateSlot(self, state, speed = None):
        com = str(self.c.com)
        if state: 
            self.logWrite(com + ' is active', 4)
        else: 
            self.logWrite(com + ' is not active', 4)
            self.comState.set(com + ' is not active')
        if state and speed != None:
            if speed == 1200 or speed == 9600:
                if str(speed) != self.config['comtest']['speed']:
                    self.config['comtest']['speed'] = str(speed)
                    configfile = open('settings.ini', 'w')
                    self.config.write(configfile)
                    configfile.close()
                    self.logWrite((com + ' speed: '+ str(speed)), 4)

    def closeEvent(self):
        if self.config.getboolean('comtest', 'enabled'):
            try:
                if self.c.state['opened']:
                    self.w.TLabel1.configure(text = "Processing shutdown...") ##Не работает, ну и ладно
                    print('try to stop, send 6')
                    self.c.sendCommand('6')
                    sleep(6)
                self.c.stop()
                self.c.t1enabled = False
            except: pass
        try: os.remove('tmp')
        except: pass
        self.logWrite('Shutdown', 1)
        try: self.p1.stop()
        except: pass
        try: self.p2.stop()
        except: pass
        self.watchdogEnabled = False
        root.destroy()
    
    def on_settingsAction_triggered(self):
        self.setWin = tk_settingsForm.create_New_Toplevel(root)[1]
        self.setWin.TButton1.configure(command = self.__save_settings)
        self.setWin.TButton2.configure(command = tk_settingsForm.destroy_New_Toplevel)
        tk_settingsForm_support.ip1.set(self.config['iptest']['ip1'])
        tk_settingsForm_support.ip2.set(self.config['iptest']['ip2'])
        tk_settingsForm_support.comPortEnabledChecked.set('1' if self.config.getboolean('comtest', 'enabled') else '0')
        tk_settingsForm_support.enableAutoSpeed.set('1' if self.config.getboolean('comtest', 'autoSpeed') else '0')
        tk_settingsForm_support.comPort.set(self.config['comtest']['port'])
        tk_settingsForm_support.comSpeed.set(self.config['comtest']['speed'])
        tk_settingsForm_support.critTemp.set(self.config['comtest']['maxtemp'])
        tk_settingsForm_support.ip1rebootChecked.set('1' if self.config.getboolean('modemsettings', 'ip1') else '0')
        tk_settingsForm_support.ip2rebootChecked.set('1' if self.config.getboolean('modemsettings', 'ip2') else '0')
        tk_settingsForm_support.maxLogSize.set(self.config['logsettings']['maxlogsize'])
        tk_settingsForm_support.ip1Log.set('1' if self.config.getboolean('logsettings', 'ip1') else '0')
        tk_settingsForm_support.ip2Log.set('1' if self.config.getboolean('logsettings', 'ip2') else '0')
        tk_settingsForm_support.sysStartUp.set('1' if self.config.getboolean('logsettings', 'onsysup') else '0')
        tk_settingsForm_support.sysShutdown.set('1' if self.config.getboolean('logsettings', 'onsysdown') else '0')
        tk_settingsForm_support.comPortLog.set('1' if self.config.getboolean('logsettings', 'com') else '0')
        tk_settingsForm_support.tempLog.set('1' if self.config.getboolean('logsettings', 'tempchange') else '0')
        
    def __save_settings(self):
        self.config['iptest']['ip1'] = tk_settingsForm_support.ip1.get()
        self.config['iptest']['ip2'] = tk_settingsForm_support.ip2.get()
        self.config['comtest']['enabled'] = 'True' if tk_settingsForm_support.comPortEnabledChecked.get() == '1' else 'False'
        self.config['comtest']['autoSpeed'] = 'True' if tk_settingsForm_support.enableAutoSpeed.get() == '1' else 'False'
        self.config['comtest']['port'] = tk_settingsForm_support.comPort.get()
        self.config['comtest']['speed'] = tk_settingsForm_support.comSpeed.get()
        self.config['comtest']['maxtemp'] = tk_settingsForm_support.critTemp.get()
        self.config['modemsettings']['ip1'] = 'True' if tk_settingsForm_support.ip1rebootChecked.get() == '1' else 'False'
        self.config['modemsettings']['ip2'] = 'True' if tk_settingsForm_support.ip2rebootChecked.get() == '1' else 'False'
        self.config['logsettings']['maxlogsize'] = tk_settingsForm_support.maxLogSize.get()
        self.config['logsettings']['onsysup'] = 'True' if tk_settingsForm_support.sysStartUp.get() == '1' else 'False'
        self.config['logsettings']['onsysdown'] = 'True' if tk_settingsForm_support.sysShutdown.get() == '1' else 'False'
        self.config['logsettings']['ip1'] = 'True' if tk_settingsForm_support.ip1Log.get() == '1' else 'False'
        self.config['logsettings']['ip2'] = 'True' if tk_settingsForm_support.ip2Log.get() == '1' else 'False'
        self.config['logsettings']['com'] = 'True' if tk_settingsForm_support.comPortLog.get() == '1' else 'False'
        self.config['logsettings']['tempchange'] = 'True' if tk_settingsForm_support.tempLog.get() == '1' else 'False'
        flags = ''
        for i in ['onsysup', 'onsysdown', 'ip1', 'ip2', 'com', 'tempchange']:
            if i != 'maxlogsize':
                if self.config['logsettings'][i] == 'True': flags += '1'
                else: flags += '0'
        self.config['logsettings']['flags'] = flags
        with open('settings.ini', 'w') as configfile: self.config.write(configfile)
        self.t3 = threading.Thread(target = self.readConfig, args = ())
        self.t3.start()
        tk_settingsForm.destroy_New_Toplevel()
        
    
    def on_restartComAction_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): 
            self.t = threading.Thread(target = self.__restartCom, args = ())
            self.t.start()
    
    def __restartCom(self):
        self.c.restart(5)
        
    
    def on_restartAllAction_triggered(self):
        if messagebox.askyesno('Query', "You have requested for hard reset. Are you sure?"):
            try: 
                self.c.sendCommand('4')
                self.logWrite('Hard reset', 4)
            except: pass
            
    def on_disableCommandsAction_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('6')
    
    def on_enableCommandsAction_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('7')
    
    def on_clearLogAction_triggered(self):
        if messagebox.askyesno('Query', 'Log would be cleaned, all information would be deleted. Are you sure?'):
            self.w.Scrolledtext1.delete(1.0, tkinter.END)
            with open('log.txt', 'w') as log: log.write('')
    
    def on_sendCommand3_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('3')
    
    def on_sendCommand5_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('5')
    
    def on_restartModemAction_toggled(self):
        p0 = tk_NetPing_support.needToRebootModem.get()
        print(p0)
        if self.config.getboolean('comtest', 'enabled') and p0 == '1': 
            self.needToRebootModem3 = True
            try: self.c.needToRebootModem = True
            except: pass
            self.logWrite('Modem restart requested', 4)
        if self.config.getboolean('comtest', 'enabled') and p0 == '0': 
            self.needToRebootModem3 = False
            try: self.c.needToRebootModem = False
            except: pass
            self.logWrite('Modem restart cancelled', 4)
    
    def on_createNewLogAction_triggered(self):
        self.w.Scrolledtext1.delete(1.0, tkinter.END)
        self.textEdit.setPlainText('')
        date = datetime.now().strftime('%d-%m-%y_%H-%M-%S')
        filename = "log-" + date + ".txt"
        os.rename('log.txt', filename)
        with open('log.txt', 'x') as log: log.write('')

    def __com_watcher(self): ## Весь метод будет задействован после перехода на Tk
        state = {'opened':False, 'temp':'', 'sleeping':0}
        while self.watchdogEnabled:
            self.w.TLabel1.configure(text = self.statusMessage)
            try:
                if self.c.state['sleeping'] != 0: 
                    print('sleeping')
                    if state['opened']:
                        self.comStateSlot(False)
                        self.comState.set(self.c.com + " закрыт")
                        state['opened'] = False
                        state['temp'] = ''
                    self.comState.set(self.c.com + " restarting after " + str(self.c.state['sleeping'])  + " sec")
                else:
                    if self.c.state['opened']  and not state['opened']: 
                        self.comStateSlot(True, self.c.state['speed'])
                        self.comState.set(self.c.com + " opened")
                        state['opened'] = self.c.state['opened']
                        self.tempChanged(self.c.state['temp'])
                    if not self.c.state['opened']  and state['opened']: 
                        self.comStateSlot(False)
                        self.comState.set(self.c.com + " closed")
                        state['opened'] = self.c.state['opened']
                    if state['opened']:
                        if self.c.state['temp'] != state['temp']: 
                            if self.c.state['temp'] != '':
                                state['temp'] = self.c.state['temp']
                                self.tempChanged(state['temp'])
                            else:
                                self.comStateSlot(False)
                                state['opened'] = False
                                self.comState.set(self.c.com + " does not response")
                try:
                    q = self.messages.get_nowait()
                    self.ipStateChanged(q[0], q[1])
                except: pass 
            except: pass
            finally: sleep(1)
    
    def __ip_watcher(self):
        while self.watchdogEnabled:
            try:
                q = self.messages.get_nowait()
                self.ipStateChanged(q[0], q[1])
            except: sleep(1) 

