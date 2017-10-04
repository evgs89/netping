# -*- coding: utf-8 -*-

"""
Module implementing netPingSettings.
"""

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog
import configparser
from .Ui_netPingSettings import Ui_Dialog


class netPingSettings(QDialog, Ui_Dialog):
    settingsChanged = pyqtSignal()
    def __init__(self, parent=None):
        super(netPingSettings, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_okButton_released(self):
        self.config = configparser.ConfigParser(allow_no_value = True)
        self.config.read('settings.ini')
        self.config['iptest']['ip1'] = self.ip1Edit.text()
        self.config['iptest']['ip2'] = self.ip2Edit.text()
        self.config['comtest']['enabled'] = str(self.comPortEnabled.isChecked())
        self.config['comtest']['port'] = self.comEdit.text()
        self.config['comtest']['speed'] = self.lineEdit_4.text()
        self.config['comtest']['maxtemp'] = self.maxTempEdit.text()
        self.config['modemsettings']['ip1'] = str(self.ip1reboot.isChecked())
        self.config['modemsettings']['ip2'] = str(self.ip2reboot.isChecked())
        flags = ''
        self.config['logsettings']['onsysup'] = str(self.sysStartUp.isChecked())
        if self.sysStartUp.isChecked(): flags += '1'
        else: flags += '0'
        self.config['logsettings']['onsysdown'] = str(self.sysShutdown.isChecked())
        if self.sysShutdown.isChecked(): flags += '1'
        else: flags += '0'
        self.config['logsettings']['ip1'] = str(self.ip1Log.isChecked())
        if self.ip1Log.isChecked(): flags += '1'
        else: flags += '0'
        self.config['logsettings']['ip2'] = str(self.ip2Log.isChecked())
        if self.ip2Log.isChecked(): flags += '1'
        else: flags += '0'
        self.config['logsettings']['com'] = str(self.comPortLog.isChecked())
        if self.comPortLog.isChecked(): flags += '1'
        else: flags += '0'
        self.config['logsettings']['tempchange'] = str(self.tempLog.isChecked())
        if self.tempLog.isChecked(): flags += '1'
        else: flags += '0'
        self.config['logsettings']['flags'] = flags
        with open('settings.ini', 'w') as configfile: self.config.write(configfile)
        self.settingsChanged.emit()
        self.close()

    
    @pyqtSlot()
    def on_cancelButton_released(self):
        self.close()
