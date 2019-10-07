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
import threading, queue
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLabel
from PyQt5.Qt import QObject

from ui.extClasses import pinger
from ui.netPingSettings import netPingSettings
from .Ui_netPing import Ui_MainWindow

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


class ComLoop:
    def __init__(self):
        super(ComLoop, self).__init__()
        self.com = None
        self.speed = None
        self.needToRebootModem = False
        self.autoChangeSpeedCounter = 3
        self.autoSpeed = None
        self.restarting = False
        self.comSendCommandQueue = queue.Queue()
        self.comEnabled = False
        self.state = {'opened': False, 'temp': '', 'sleeping': 0, 'speed': self.speed}
        self.queue = queue.Queue()
        self.t1enabled = True
        self.t1 = threading.Thread(target=self.__queueHandler, args=(self.queue,))
        self.t1.start()
    
    def start(self, delay=0):
        if not self.needToRebootModem:
            self.comSendCommandQueue.put('1')
        else:
            self.comSendCommandQueue.put('2')
        self.comEnabled = True
        self.t = threading.Thread(target=self.__comLoop, args=(delay, ))
        self.t.start()
        return(0)
    
    def settingsChanged(self, com, speed, auto=True):
        try:
            if self.ser.port != com or self.speed != speed or auto != self.autoSpeed:
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
        except:
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
    
    def _clear_com_send_command_queue(self):
        while not self.comSendCommandQueue.empty():
            self.comSendCommandQueue.get_nowait()

    def restart(self, delay=10):
        self._clear_com_send_command_queue()
        if not self.restarting:
            self.restarting = True
            print('restarting COM, delay = ' + str(delay))
            if self.stop() == 0: 
                self.state = {'opened': False, 'temp': '', 'sleeping': delay, 'speed': self.speed}
                print('com restart, delay = ' + str(delay))
                self.start(delay)
    
    def auto_change_speed(self):
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
        elif not self.autoSpeed and self.comEnabled:
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
        print(self.com + ' отправлена команда ' + command)
        self.comSendCommandQueue.put(command)
    
    def __comLoop(self, delay): #, com, speed, auto): #queue, commandQueue,, comEnabled
        self.queue.put(['message', 'ComLoop started'])
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
                        if counter >= 2 and self.comEnabled:
                        # Количество повторений отправки команд, можно попробовать уменьшить для увеличения
                        # скорости отклика, но есть риск непрохождения команды
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
                    if msg[1] == 'autoChangeSpeed': self.auto_change_speed()
                    elif msg[1] == 'DisableAutoSpeed': self.autoSpeed = False
                elif msg[0] == 'sleep': self.state['sleeping'] = msg[1]
                else: pass
            except:
                sleep(.3)

class comStateWatcher(QObject):
    comStateChanged = pyqtSignal(bool, int)
    comStateText = pyqtSignal(str)
    tempChanged = pyqtSignal(str)
    def __init__(self, com):
        super(comStateWatcher, self).__init__()
        self.enabled = True
        self.state = {'opened': False, 'temp': '', 'sleeping': 0}
    
    def changeCom(self, com, delay = 0):
        sleep(delay)
        self.enabled = False
        try:
            while self.t.is_active: sleep(.1)
        except: pass
        self.enabled = True
        self.c = com
        self.c_name = com.com
        self.t = threading.Thread(target = self.__mainLoop, args = ())
        self.t.start()
        
    def __mainLoop(self):
        while self.enabled:
            try:
                if self.c.state['sleeping'] != 0: 
                    print('sleeping')
                    if self.state['opened']:
                        self.comStateChanged.emit(False, None)
                        self.comStateText.emit(self.c.com + " закрыт")
                        self.state['opened'] = False
                        self.state['temp'] = ''
                    self.comStateText.emit(self.c.com + " перезапуск через " + str(self.c.state['sleeping'])  + " сек")
                else:
                    if not self.c.state['opened']  and not self.state['opened']: self.comStateText.emit(self.c.com + " открываем")
                    if self.c.state['opened']  and not self.state['opened']: 
                        self.comStateChanged.emit(True, self.c.state['speed'])
                        self.comStateText.emit(self.c.com + " открыт")
                        self.state['opened'] = self.c.state['opened']
                    if not self.c.state['opened']  and self.state['opened']: 
                        self.comStateChanged.emit(False, None)
                        self.comStateText.emit(self.c.com + " закрыт")
                        self.state['opened'] = self.c.state['opened']
                    if self.state['opened']:
                        if self.c.state['temp'] != self.state['temp']: 
                            if self.c.state['temp'] != '':
                                self.state['temp'] = self.c.state['temp']
                                self.tempChanged.emit(self.state['temp'])
                            else:
                                self.comStateText.emit(self.c.com + " не отвечает")
                sleep(1)
            except:
                print('comWatcher ERROR')
                self.comStateChanged.emit(False, None)
                self.comStateText.emit(self.c_name + " закрыт")
                self.enabled = False
        print('comWatcher STOPPED')
        return(0)

class MainWindow(QMainWindow, Ui_MainWindow): #class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.log = ""
        self.watchdogEnabled = True
        self.c = ComLoop()
        self.createComWatcher(self.c)
        self.readConfig()
        try: 
            with open('tmp') as tmp: self.logWrite('Неожиданное выкл-е', 1, tmp.read())
        except FileNotFoundError: pass
        except: self.logWrite('Неожиданное выкл-е', 1, '')
        self.t1 = threading.Thread(target = self.watchdog, args = ())
        self.t1.daemon = True
        self.t1.start()
        self.logWrite('Запуск', 0)
    

    def readConfig(self):
        self.config = configparser.ConfigParser(allow_no_value = True)
        while self.indicatorsLayout.count():
            item = self.indicatorsLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
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
            self.comState = QLabel(self.centralWidget)
            self.comState.setObjectName("comState")
            self.indicatorsLayout.addWidget(self.comState)
            self.restartComAction.setEnabled(True)
            self.restartModemAction.setEnabled(True)
            self.disableCommandsAction.setEnabled(True)
            self.restartAllAction.setEnabled(True)
            self.enableCommandsAction.setEnabled(True)
            self.sendCommand3.setEnabled(True)  
            self.sendCommand5.setEnabled(True)
            self.comStateChanged('Запускаем ' + self.config['comtest']['port'])
            print('changing settings of ComLoop')
            self.c.settingsChanged(self.config['comtest']['port'], self.config['comtest']['speed'], self.config.getboolean('comtest', 'autoSpeed'))
            self.cw.changeCom(self.c, 1)
        else:
            self.restartComAction.setEnabled(False)
            self.restartModemAction.setEnabled(False)
            self.disableCommandsAction.setEnabled(False)
            self.restartAllAction.setEnabled(False)
            self.enableCommandsAction.setEnabled(False)
            self.sendCommand3.setEnabled(False)  
            self.sendCommand5.setEnabled(False) 
            try: 
                self.cw.enabled = False
                self.c.stop()
            except: pass
        if self.config['iptest']['ip1'] != '':
            self.ip1State = QLabel(self.centralWidget)
            self.ip1State.setObjectName("ip1State")
            self.indicatorsLayout.addWidget(self.ip1State)
            self.ip1 = self.config['iptest']['ip1']
            self.p1 = pinger(self.ip1, 5)
            self.ip1State.setText(self.ip1 + ' не отвечает')
            self.p1.stateChangedSignal.connect(self.ipStateChanged)
            self.ipStateChanged( self.ip1, False)
            self.p1.start()
        else: 
            try: self.p1.stop()
            except: pass
        if self.config['iptest']['ip2'] != '':
            self.ip2State = QLabel(self.centralWidget)
            self.ip2State.setObjectName("ip2State")
            self.indicatorsLayout.addWidget(self.ip2State)
            self.ip2 = self.config['iptest']['ip2']
            self.p2 = pinger(self.ip2, 5)
            self.ip1State.setText(self.ip1 + ' не отвечает')
            self.p2.stateChangedSignal.connect(self.ipStateChanged)
            self.ipStateChanged( self.ip2, False)
            self.p2.start()
        else: 
            try: self.p2.stop()
            except: pass
        
    def createComWatcher(self, com):
        self.cw = comStateWatcher(com)
        self.cw.tempChanged.connect(self.tempChanged)
        self.cw.comStateText.connect(self.comStateChanged)
        self.cw.comStateChanged.connect(self.comStateSlot)
        
    def ipStateChanged(self, ip, state):
        try:
            if ip == self.ip1: 
                label = self.ip1State
                logcat = 2
                if self.config.getboolean('modemsettings', 'ip1'):
                    if not state and self.config.getboolean('modemsettings', 'ip1'): self.needToRebootModem1 = True
                    if state: self.needToRebootModem1 = False
            if ip == self.ip2:
                label = self.ip2State
                logcat = 3
                if self.config.getboolean('modemsettings', 'ip2'):
                    if not state and self.config.getboolean('modemsettings', 'ip2'): self.needToRebootModem2 = True
                    if state: self.needToRebootModem2 = False
        except: pass
        if self.config.getboolean('comtest', 'enabled') == True: self.c.needToRebootModem = bool(self.needToRebootModem1 + self.needToRebootModem2 + self.needToRebootModem3)
        if state: text = ip + ' доступен'
        else: text = ip + ' недоступен'
        label.setText(text)
        self.logWrite(text, logcat)
    
    def logWrite(self, text, category, time = None):
        self.statusMessage.setText(text)
        if time == None: dt = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        else: dt = time
        with open('log.txt',  'a', newline='') as logfile:
            logwriter = csv.writer(logfile, dialect='unix')
            logwriter.writerow([category, dt, text])
            if self.config['logsettings']['flags'][category] == '1': 
                self.log += (dt + ' ' + text + '\n')
        self.__log_refresh()
    
    def logRead(self):
        try:
            a = open('log.txt', 'x')
            a.write('')
            a.close()
        except FileExistsError:
            if os.path.getsize('log.txt') > int(self.config['logsettings']['maxlogsize']):
                self.on_createNewLogAction_triggered()
                self.logWrite('Лог слишком большой, начат новый',  1)
        with open('log.txt', newline = '') as logfile: #read log
            self.log = ""
            try:
                logreader = csv.reader(logfile, dialect = "unix")
                for row in logreader:
                    if self.config['logsettings']['flags'][int(row[0])] == '1':
                        self.log += (row[1] + ' ' + row[2] + '\n')
                self.__log_refresh()
            except:
                logfile.close()
                self.on_createNewLogAction_triggered()
                self.logWrite('Лог повреждён, начат новый',  1)
                with open('log.txt', newline = '') as logfile: #read log
                    self.log = ""
                    self.log += (datetime.now().strftime('%d/%m/%y %H:%M:%S') + ' Лог повреждён, начат новый' + '\n')
    
    def __log_refresh(self):
        self.textEdit.setPlainText(self.log)
        self.cur = self.textEdit.textCursor()
        self.cur.movePosition(QTextCursor.End)
        self.textEdit.setTextCursor(self.cur)
        
    
    def watchdog(self):
        sleeping = 0
        while self.watchdogEnabled:
            if not sleeping:
                tmpfile = open('tmp', 'w')
                tmpfile.write(datetime.now().strftime('%d/%m/%y %H:%M:%S'))
                tmpfile.close()
                self.statusMessage.setText(datetime.now().strftime('%H:%M %d/%m') + ' контроль активен')
                try:
                    if self.c.needToRebootModem: self.statusMessage.setText(datetime.now().strftime('%H:%M %d/%m') + ' ждём перезагрузки модема')
                except: pass
                finally: sleeping = 15
            else:
                sleeping -= 1
                sleep(1)
            
    def comStateChanged(self, text):
        self.comState.setText(text)
        
    def tempChanged(self, temp):
        self.comState.setText(self.c.com + ' активен, t = ' + temp)
        self.statusMessage.setText(datetime.now().strftime('%H:%M:%S %d/%m') + ' t = ' + temp)
        if len(temp) == 3: 
            self.logWrite(('t = ' + str(temp)), 5)
            if int(temp[1:]) >= int(self.config['comtest']['maxtemp']): 
                self.logWrite('ПРЕВЫШЕНИЕ КРИТ. ТЕМПЕРАТУРЫ', 4)
                self.c.sendCommand('4')
        
    def comStateSlot(self, state, speed = None):
        com = str(self.c.com)
        if state: 
            self.logWrite(com + ' активен', 4)
        else: 
            self.logWrite(com + ' неактивен', 4)
            self.comState.setText(com + ' неактивен')
        if state and speed != None:
            if speed == 1200 or speed == 9600:
                if str(speed) != self.config['comtest']['speed']:
                    self.config['comtest']['speed'] = str(speed)
                    configfile = open('settings.ini', 'w')
                    self.config.write(configfile)
                    configfile.close()
                    self.logWrite((com + ' скорость: '+ str(speed)), 4)

    @pyqtSlot()
    def closeEvent(self, event):
        if self.config.getboolean('comtest', 'enabled'):
            try:
                if self.c.state['opened']:
                    self.comState.setText("Завершение работы...")
                    print('try to stop, send 6')
                    self.c.sendCommand('6')
                    self.cw.comStateText.disconnect()
                    sleep(6)
                self.c.stop()
                self.c.t1enabled = False
            except: pass
        try: os.remove('tmp')
        except: pass
        self.logWrite('Выключение', 1)
        try: self.p1.stop()
        except: pass
        try: self.p2.stop()
        except: pass
        self.watchdogEnabled = False
        self.cw.enabled = False
        event.accept()
    
    @pyqtSlot()
    def on_settingsAction_triggered(self):
        self.setWin = netPingSettings(self)
        self.setWin.ip1Edit.setText(self.config['iptest']['ip1'])
        self.setWin.ip2Edit.setText(self.config['iptest']['ip2'])
        self.setWin.comPortEnabled.setChecked(self.config.getboolean('comtest', 'enabled'))
        self.setWin.enableAutoSpeedCheckbox.setChecked(self.config.getboolean('comtest', 'autoSpeed'))
        self.setWin.comEdit.setText(self.config['comtest']['port'])
        self.setWin.lineEdit_4.setText(self.config['comtest']['speed'])
        self.setWin.maxTempEdit.setText(self.config['comtest']['maxtemp'])
        self.setWin.ip1reboot.setChecked(self.config.getboolean('modemsettings', 'ip1'))
        self.setWin.ip2reboot.setChecked(self.config.getboolean('modemsettings', 'ip2'))
        self.setWin.maxLogSize.setValue(int(self.config['logsettings']['maxlogsize']))
        self.setWin.ip1Log.setChecked(self.config.getboolean('logsettings', 'ip1'))
        self.setWin.ip2Log.setChecked(self.config.getboolean('logsettings', 'ip2'))
        self.setWin.sysStartUp.setChecked(self.config.getboolean('logsettings', 'onsysup'))
        self.setWin.sysShutdown.setChecked(self.config.getboolean('logsettings', 'onsysdown'))
        self.setWin.comPortLog.setChecked(self.config.getboolean('logsettings', 'com'))
        self.setWin.tempLog.setChecked(self.config.getboolean('logsettings', 'tempchange'))
        self.setWin.settingsChanged.connect(self.readConfig)
        self.setWin.show()
        
    
    @pyqtSlot()
    def on_restartComAction_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): 
            self.t = threading.Thread(target = self.__restartCom, args = ())
            self.t.start()
    
    def __restartCom(self):
        self.c.restart(5)
        self.cw.changeCom(self.c, 1)
        
    
    @pyqtSlot()
    def on_restartAllAction_triggered(self):
        acq = QMessageBox.question(self, 'Запрос', 'Комплекс будет перезапущен. Вы уверены?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if acq == QMessageBox.Yes:
            try: 
                self.c.sendCommand('4')
                self.logWrite('Перезапуск комплекса', 4)
            except: pass
            
    @pyqtSlot()
    def on_disableCommandsAction_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('6')
    
    @pyqtSlot()
    def on_enableCommandsAction_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('7')
    
    @pyqtSlot()
    def on_clearLogAction_triggered(self):
        acq = QMessageBox.question(self, 'Запрос', 'Лог будет очищен. Вы уверены?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if acq == QMessageBox.Yes:
            self.log = ''
            self.textEdit.setPlainText('')
            with open('log.txt', 'w') as log: log.write('')
    
    @pyqtSlot()
    def on_sendCommand3_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('3')
    
    @pyqtSlot()
    def on_sendCommand5_triggered(self):
        if self.config.getboolean('comtest', 'enabled'): self.c.sendCommand('5')
    
    @pyqtSlot(bool)
    def on_restartModemAction_toggled(self, p0):
        if self.config.getboolean('comtest', 'enabled') and p0: 
            self.needToRebootModem3 = True
            try: self.c.needToRebootModem = True
            except: pass
            self.logWrite('Задан перезапуск модема', 4)
        if self.config.getboolean('comtest', 'enabled') and not p0: 
            self.needToRebootModem3 = False
            try: self.c.needToRebootModem = False
            except: pass
            self.logWrite('Отменён перезапуск модема', 4)
    
    @pyqtSlot()
    def on_createNewLogAction_triggered(self):
        self.log = ""
        self.textEdit.setPlainText('')
        date = datetime.now().strftime('%d-%m-%y_%H-%M-%S')
        filename = "log-" + date + ".txt"
        os.rename('log.txt', filename)
        with open('log.txt', 'x') as log: log.write('')
    
    @pyqtSlot()
    def on_programInfoAction_triggered(self):
        QMessageBox.information(self, 'О программе', 'Версия 1.4 (27.11.2018)', QMessageBox.Ok | QMessageBox.NoButton | QMessageBox.NoButton, QMessageBox.Ok)
    
    def __com_watcher(self): ## Весь метод будет задействован после перехода на Tk
        state = {'opened':False, 'temp':'', 'sleeping':0}
        while self.watchdogEnabled:
            try:
                if self.c.state['sleeping'] != 0: 
                    print('sleeping')
                    if state['opened']:
                        self.comStateSlot(False)
                        self.comState.setText(self.c.com + " закрыт")
                        state['opened'] = False
                        state['temp'] = ''
                    self.comState.setText(self.c.com + " перезапуск через " + str(self.c.state['sleeping'])  + " сек")
                else:
                    if self.c.state['opened']  and not state['opened']: 
                        self.comStateSlot(True, self.c.state['speed'])
                        self.comState.setText(self.c.com + " открыт")
                        state['opened'] = self.c.state['opened']
                        self.tempChanged(self.c.state['temp'])
                    if not self.c.state['opened']  and state['opened']: 
                        self.comStateSlot(False)
                        self.comState.setText(self.c.com + " закрыт")
                        state['opened'] = self.c.state['opened']
                    if state['opened']:
                        if self.c.state['temp'] != state['temp']: 
                            if self.c.state['temp'] != '':
                                state['temp'] = self.c.state['temp']
                                self.tempChanged(state['temp'])
                            else:
                                self.comStateSlot(False)
                                state['opened'] = False
                                self.comState.setText(self.c.com + " не отвечает")
                sleep(1)
            except:
                sleep(1)

