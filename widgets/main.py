# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1959, 640)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButtonLocalCamera = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonLocalCamera.setGeometry(QtCore.QRect(10, 10, 211, 31))
        self.pushButtonLocalCamera.setObjectName("pushButtonLocalCamera")
        self.pushButtonConnect = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonConnect.setEnabled(False)
        self.pushButtonConnect.setGeometry(QtCore.QRect(440, 10, 211, 31))
        self.pushButtonConnect.setObjectName("pushButtonConnect")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 50, 1941, 531))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayoutConference = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayoutConference.setContentsMargins(0, 0, 0, 0)
        self.gridLayoutConference.setHorizontalSpacing(2)
        self.gridLayoutConference.setVerticalSpacing(1)
        self.gridLayoutConference.setObjectName("gridLayoutConference")
        self.lineEditConnectionIP = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditConnectionIP.setEnabled(False)
        self.lineEditConnectionIP.setGeometry(QtCore.QRect(660, 10, 181, 31))
        self.lineEditConnectionIP.setObjectName("lineEditConnectionIP")
        self.pushButtonOpenConection = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonOpenConection.setEnabled(False)
        self.pushButtonOpenConection.setGeometry(QtCore.QRect(230, 10, 201, 31))
        self.pushButtonOpenConection.setObjectName("pushButtonOpenConection")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1959, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Skllat"))
        self.pushButtonLocalCamera.setText(_translate("MainWindow", "Включить камеру"))
        self.pushButtonConnect.setText(_translate("MainWindow", "Подключиться"))
        self.lineEditConnectionIP.setPlaceholderText(_translate("MainWindow", "127.0.0.1"))
        self.pushButtonOpenConection.setText(_translate("MainWindow", "Открыть соединение"))

