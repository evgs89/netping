# -*- coding: utf-8 -*-

"""
Module implementing tempLogView.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from .Ui_tempLogView import Ui_Dialog


class tempLogView(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        super(tempLogView, self).__init__(parent)
        self.setupUi(self)
        self.filename = ''
    
    @pyqtSlot()
    def on_clear_released(self):
        log = open(self.filename, 'w')
        log.write('')
        log.close()
        self.log.setPlainText('')
