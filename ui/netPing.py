# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLabel
from PyQt5.QtGui import QTextCursor
from PyQt5.Qt import QObject
from time import sleep
import serial, configparser, os, threading, csv
from datetime import datetime

from .Ui_netPing import Ui_MainWindow
from ui.tempLogView import tempLogView
from ui.netPingSettings import netPingSettings
from ui.extClasses import pinger
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


class comLoop(QObject):
    tempChangedSignal = pyqtSignal(str)
    statusMessage = pyqtSignal(str)
    comStateSignal = pyqtSignal(bool)
    comState = False
    def __init__(self, com, speed, delay = 0):
        super(comLoop, self).__init__()
        self.delay = delay
        self.com = com
        self.speed = speed
        self.needToRebootModem = False
    
    def start(self):
        if not self.needToRebootModem: self.comSendCommand = '1'
        else: self.comSendCommand = '2'
        self.t = threading.Thread(target = self.__comLoop, args = ())
        self.t.daemon = True
        self.t.start()

    def settingsChanged(self, com, speed):
        self.com = com
        self.speed = speed
        self.restart(3)
    
    def restart(self, delay=10):
        self.statusMessage.emit(self.com + ' перезапуск, ' + str(delay) + ' сек')
        self.comEnabled = False
        self.delay = delay
        print('com restart, delay = ' + str(delay))
        self.start()
    
    def stop(self):
        self.comEnabled = False
        
    def sendCommand(self, command):
        self.statusMessage.emit(self.com + ' отправлена команда ' + command)
        self.comSendCommand = command
    
    def __comLoop(self):
        sleep(self.delay)
        self.comEnabled = True
        self.temp = '0'
        try: 
            self.ser = serial.Serial(self.com)
            self.ser.baudrate = self.speed
            self.ser.timeout = 1
            counter = 0
            if self.ser.readline(): self.statusMessage.emit(self.com + ' активен')
            while self.comEnabled:
                if self.ser.readline() == b'': 
                    print('read empty')
                    if self.comState:
                        self.comStateSignal.emit(False)
                        self.comState = False
                    self.restart(2)
                else:
                    temp = self.ser.readline().decode('ascii')
                    self.ser.write(bytes(self.comSendCommand, 'ascii'))
                    print(temp, " ", self.comSendCommand) ##DIAG
                    self.statusMessage.emit(self.com + ' активен, t = ' + temp)
                    if self.comSendCommand != '1' and self.comSendCommand != '2':
                        counter += 1
                        if counter >= 3:
                            if not self.needToRebootModem: self.comSendCommand = '1'
                            else: self.comSendCommand = '2'
                    else: 
                        counter = 0
                        if not self.needToRebootModem: self.comSendCommand = '1'
                        else: self.comSendCommand = '2'
                    if len(temp) == 3:
                        if not self.comState:
                            self.comState = True
                            self.comStateSignal.emit(True)
                        if temp != self.temp:
                            self.temp = temp
                            self.tempChangedSignal.emit(temp)
            self.ser.close()
            if self.comState: 
                self.comStateSignal.emit(False)
                self.comState = False
            self.statusMessage.emit(self.com + ' закрыт')
        except: 
            self.ser.close()
            print(str(Exception))
            self.restart(1)
        
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.log = ""
        self.watchdogEnabled = True
        self.readConfig()
        try: 
            with open('tmp') as tmp: self.logWrite('Неожиданное выкл-е', 1, tmp.read())
        except: pass
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
            self.config['comtest']['maxtemp'] = '70'
            self.config['logsettings'] = {}
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
        if self.config.getboolean('comtest', 'enabled') == True:
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
            try:
                self.c.settingsChanged(self.config['comtest']['port'], self.config['comtest']['speed'])
            except:
                self.c = comLoop(self.config['comtest']['port'], self.config['comtest']['speed'])
                self.c.tempChangedSignal.connect(self.tempChanged)
                self.c.statusMessage.connect(self.comStateChanged)
                self.c.comStateSignal.connect(self.comStateSlot)
                self.c.start()
        else:
            self.restartComAction.setEnabled(False)
            self.restartModemAction.setEnabled(False)
            self.disableCommandsAction.setEnabled(False)
            self.restartAllAction.setEnabled(False)
            self.enableCommandsAction.setEnabled(False)
            self.sendCommand3.setEnabled(False)  
            self.sendCommand5.setEnabled(False) 
            #self.comStateChanged('Работа с COM отключена')
            try: 
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
        if time == None: dt = datetime.now().strftime('%H:%M:%S %d/%m/%y')
        else: dt = time
        with open('log.txt',  'a', newline='') as logfile:
            logwriter = csv.writer(logfile, dialect='unix')
            logwriter.writerow([category, dt, text])
            if self.config['logsettings']['flags'][category] == '1': 
                self.log += (dt + ' ' + text + '\n')
                self.textEdit.setPlainText(self.log)
        self.cur = self.textEdit.textCursor()
        self.cur.movePosition(QTextCursor.End)
        self.textEdit.setTextCursor(self.cur)
    
    def logRead(self):
        with open('log.txt', newline = '') as logfile:
            self.log = ""
            logreader = csv.reader(logfile, dialect = "unix")
            for row in logreader:
                if self.config['logsettings']['flags'][int(row[0])] == '1':
                    self.log += (row[1] + ' ' + row[2] + '\n')
            self.textEdit.setPlainText(self.log)
            self.cur = self.textEdit.textCursor()
            self.cur.movePosition(QTextCursor.End)
            self.textEdit.setTextCursor(self.cur)
        
    def watchdog(self):
        while self.watchdogEnabled:
            tmpfile = open('tmp', 'w')
            tmpfile.write(datetime.now().strftime('%H:%M:%S %d/%m/%y'))
            tmpfile.close()
            self.statusMessage.setText(datetime.now().strftime('%H:%M %d/%m') + ' контроль активен')
            try: 
                if self.c.needToRebootModem: self.statusMessage.setText(datetime.now().strftime('%H:%M %d/%m') + ' ждём перезагрузки модема')
            except: pass
            sleep(60)
            
    def comStateChanged(self, text):
        self.comState.setText(text)
        
    def tempChanged(self, temp):
        self.comState.setText(self.c.com + ' активен, t = ' + temp)
        self.statusMessage.setText(datetime.now().strftime('%H:%M:%S %d/%m') + ' t = ' + temp)
        self.logWrite(('t = ' + temp), 5)
        if int(temp[1:]) >= int(self.config['comtest']['maxtemp']): 
            self.logWrite('ПРЕВЫШЕНИЕ КРИТ. ТЕМПЕРАТУРЫ', 4)
            self.c.sendCommand('4')
        
    def comStateSlot(self, state):
        if state: self.logWrite((self.c.com + ' активен'), 4)
        else: self.logWrite((self.c.com + ' неактивен'), 4)

    @pyqtSlot()
    def closeEvent(self, event):
        try: self.p1.stop()
        except: pass
        try: self.p2.stop()
        except: pass
        self.watchdogEnabled = False
        try: os.remove('tmp')
        except: pass
        try: self.c.stop()
        except: pass
        self.logWrite('Выключение', 1)
        event.accept()
    
    @pyqtSlot()
    def on_settingsAction_triggered(self):
        self.setWin = netPingSettings(self)
        self.setWin.ip1Edit.setText(self.config['iptest']['ip1'])
        self.setWin.ip2Edit.setText(self.config['iptest']['ip2'])
        self.setWin.comPortEnabled.setChecked(self.config.getboolean('comtest', 'enabled'))
        self.setWin.comEdit.setText(self.config['comtest']['port'])
        self.setWin.lineEdit_4.setText(self.config['comtest']['speed'])
        self.setWin.maxTempEdit.setText(self.config['comtest']['maxtemp'])
        self.setWin.ip1reboot.setChecked(self.config.getboolean('modemsettings', 'ip1'))
        self.setWin.ip2reboot.setChecked(self.config.getboolean('modemsettings', 'ip2'))
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
        if self.config.getboolean('comtest', 'enabled'): self.c.restart(10)
        
    
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
        with open('log.txt') as log:
            logcontent = log.read()
        date = datetime.now().strftime('%d-%m-%y')
        filename = "log-" + date + ".txt"
        with open(filename, 'w') as newlog: newlog.write(logcontent)
        with open('log.txt', 'w') as log: log.write('')
        
