# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/es89/Dropbox/Projects/Python/NetPing/ui/netPing.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(253, 311)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/1/icons/notification.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setDocumentMode(False)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.indicatorsLayout = QtWidgets.QVBoxLayout()
        self.indicatorsLayout.setObjectName("indicatorsLayout")
        self.verticalLayout.addLayout(self.indicatorsLayout)
        self.textEdit = QtWidgets.QTextEdit(self.centralWidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.statusMessage = QtWidgets.QLabel(self.centralWidget)
        self.statusMessage.setObjectName("statusMessage")
        self.verticalLayout.addWidget(self.statusMessage)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 253, 23))
        self.menuBar.setObjectName("menuBar")
        self.menu = QtWidgets.QMenu(self.menuBar)
        self.menu.setObjectName("menu")
        self.menu_3 = QtWidgets.QMenu(self.menu)
        self.menu_3.setObjectName("menu_3")
        self.menu_2 = QtWidgets.QMenu(self.menuBar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menuBar)
        self.settingsAction = QtWidgets.QAction(MainWindow)
        self.settingsAction.setObjectName("settingsAction")
        self.restartComAction = QtWidgets.QAction(MainWindow)
        self.restartComAction.setObjectName("restartComAction")
        self.restartModemAction = QtWidgets.QAction(MainWindow)
        self.restartModemAction.setCheckable(True)
        self.restartModemAction.setObjectName("restartModemAction")
        self.restartAllAction = QtWidgets.QAction(MainWindow)
        self.restartAllAction.setObjectName("restartAllAction")
        self.disableCommandsAction = QtWidgets.QAction(MainWindow)
        self.disableCommandsAction.setObjectName("disableCommandsAction")
        self.enableCommandsAction = QtWidgets.QAction(MainWindow)
        self.enableCommandsAction.setObjectName("enableCommandsAction")
        self.clearLogAction = QtWidgets.QAction(MainWindow)
        self.clearLogAction.setObjectName("clearLogAction")
        self.sendCommand3 = QtWidgets.QAction(MainWindow)
        self.sendCommand3.setObjectName("sendCommand3")
        self.sendCommand5 = QtWidgets.QAction(MainWindow)
        self.sendCommand5.setObjectName("sendCommand5")
        self.viewTempLogAction = QtWidgets.QAction(MainWindow)
        self.viewTempLogAction.setObjectName("viewTempLogAction")
        self.createNewLogAction = QtWidgets.QAction(MainWindow)
        self.createNewLogAction.setObjectName("createNewLogAction")
        self.menu_3.addAction(self.sendCommand3)
        self.menu_3.addAction(self.sendCommand5)
        self.menu.addAction(self.restartComAction)
        self.menu.addSeparator()
        self.menu.addAction(self.restartModemAction)
        self.menu.addAction(self.restartAllAction)
        self.menu.addAction(self.disableCommandsAction)
        self.menu.addAction(self.enableCommandsAction)
        self.menu.addAction(self.menu_3.menuAction())
        self.menu_2.addAction(self.settingsAction)
        self.menu_2.addAction(self.createNewLogAction)
        self.menu_2.addAction(self.clearLogAction)
        self.menuBar.addAction(self.menu.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Work with controller"))
        self.statusMessage.setText(_translate("MainWindow", "Система активна"))
        self.menu.setTitle(_translate("MainWindow", "Послать команду"))
        self.menu_3.setTitle(_translate("MainWindow", "Другие (резерв)"))
        self.menu_2.setTitle(_translate("MainWindow", "Дополнительно"))
        self.settingsAction.setText(_translate("MainWindow", "Настройки"))
        self.restartComAction.setText(_translate("MainWindow", "Перезапустить COM"))
        self.restartModemAction.setText(_translate("MainWindow", "Перезагрузить модем (2)"))
        self.restartAllAction.setText(_translate("MainWindow", "Полный перезапуск комплекса (4)"))
        self.disableCommandsAction.setText(_translate("MainWindow", "Отключить приём команд (6)"))
        self.enableCommandsAction.setText(_translate("MainWindow", "Включить приём команд (7)"))
        self.clearLogAction.setText(_translate("MainWindow", "Очистить текущий лог"))
        self.sendCommand3.setText(_translate("MainWindow", "3"))
        self.sendCommand5.setText(_translate("MainWindow", "5"))
        self.viewTempLogAction.setText(_translate("MainWindow", "Просмотреть лог температуры"))
        self.createNewLogAction.setText(_translate("MainWindow", "Начать новый лог"))

import ui.icons_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

