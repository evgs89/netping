# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/es89/Dropbox/Projects/Python/NetPing/ui/netPingSettings.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.WindowModal)
        Dialog.resize(410, 530)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setSizeGripEnabled(True)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 394, 518))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.ip1reboot = QtWidgets.QCheckBox(self.layoutWidget)
        self.ip1reboot.setObjectName("ip1reboot")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ip1reboot)
        self.ip1Edit = QtWidgets.QLineEdit(self.layoutWidget)
        self.ip1Edit.setObjectName("ip1Edit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ip1Edit)
        self.ip2reboot = QtWidgets.QCheckBox(self.layoutWidget)
        self.ip2reboot.setObjectName("ip2reboot")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.ip2reboot)
        self.ip2Edit = QtWidgets.QLineEdit(self.layoutWidget)
        self.ip2Edit.setObjectName("ip2Edit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ip2Edit)
        self.comPortEnabled = QtWidgets.QCheckBox(self.layoutWidget)
        self.comPortEnabled.setObjectName("comPortEnabled")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.comPortEnabled)
        self.comEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.comEdit.setObjectName("comEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comEdit)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_4)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.maxTempEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.maxTempEdit.setObjectName("maxTempEdit")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.maxTempEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comSpeed = QtWidgets.QLabel(self.layoutWidget)
        self.comSpeed.setObjectName("comSpeed")
        self.horizontalLayout.addWidget(self.comSpeed)
        self.enableAutoSpeedCheckbox = QtWidgets.QCheckBox(self.layoutWidget)
        self.enableAutoSpeedCheckbox.setObjectName("enableAutoSpeedCheckbox")
        self.horizontalLayout.addWidget(self.enableAutoSpeedCheckbox)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.formLayout_3 = QtWidgets.QFormLayout()
        self.formLayout_3.setObjectName("formLayout_3")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.maxLogSize = QtWidgets.QSpinBox(self.layoutWidget)
        self.maxLogSize.setMaximum(1048576000)
        self.maxLogSize.setProperty("value", 1048576)
        self.maxLogSize.setObjectName("maxLogSize")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.maxLogSize)
        self.verticalLayout.addLayout(self.formLayout_3)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.sysStartUp = QtWidgets.QCheckBox(self.layoutWidget)
        self.sysStartUp.setObjectName("sysStartUp")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.sysStartUp)
        self.sysShutdown = QtWidgets.QCheckBox(self.layoutWidget)
        self.sysShutdown.setObjectName("sysShutdown")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sysShutdown)
        self.ip1Log = QtWidgets.QCheckBox(self.layoutWidget)
        self.ip1Log.setObjectName("ip1Log")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.ip1Log)
        self.ip2Log = QtWidgets.QCheckBox(self.layoutWidget)
        self.ip2Log.setObjectName("ip2Log")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ip2Log)
        self.comPortLog = QtWidgets.QCheckBox(self.layoutWidget)
        self.comPortLog.setObjectName("comPortLog")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.comPortLog)
        self.tempLog = QtWidgets.QCheckBox(self.layoutWidget)
        self.tempLog.setObjectName("tempLog")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.tempLog)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.setContentsMargins(0, 0, 0, 0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        spacerItem = QtWidgets.QSpacerItem(131, 31, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(self.layoutWidget)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.hboxlayout)
        self.layoutWidget.raise_()

        self.retranslateUi(Dialog)
        self.okButton.clicked.connect(Dialog.accept)
        self.cancelButton.clicked.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Настройки"))
        self.ip1reboot.setText(_translate("Dialog", "IP1"))
        self.ip2reboot.setText(_translate("Dialog", "IP2"))
        self.comPortEnabled.setText(_translate("Dialog", "Контролировать COM-порт?"))
        self.label_4.setText(_translate("Dialog", "Критическая температура"))
        self.comSpeed.setText(_translate("Dialog", "COM-speed"))
        self.enableAutoSpeedCheckbox.setText(_translate("Dialog", "auto"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:9pt;\">При недоступности отмеченных &quot;галочкой&quot; IP адресов будет подаваться команда перезагрузки модема. </span></p><p><span style=\" font-size:9pt;\">При снятии &quot;галочки&quot; контроля COM-порта обмен данными с внешней платой осуществляться не будет.</span></p><p><span style=\" font-size:9pt;\">Если температура на датчике платы превысит указанную в качестве КРИТИЧЕСКОЙ, будет отдаваться команда на перезагрузку.</span></p></body></html>"))
        self.label.setText(_translate("Dialog", "Максим. размер лога (в байтах)  "))
        self.label_5.setText(_translate("Dialog", "События, отображаемые в логе:"))
        self.sysStartUp.setText(_translate("Dialog", "Запуск системы"))
        self.sysShutdown.setText(_translate("Dialog", "Выключение"))
        self.ip1Log.setText(_translate("Dialog", "Доступность IP1"))
        self.ip2Log.setText(_translate("Dialog", "Доступность IP2"))
        self.comPortLog.setText(_translate("Dialog", "Доступность COM"))
        self.tempLog.setText(_translate("Dialog", "Изменение температуры"))
        self.okButton.setText(_translate("Dialog", "&OK"))
        self.cancelButton.setText(_translate("Dialog", "&Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

