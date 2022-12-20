# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_secondmainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SecondMainWindow(object):
    def setupUi(self, SecondMainWindow):
        SecondMainWindow.setObjectName("SecondMainWindow")
        SecondMainWindow.resize(445, 473)
        self.centralwidget = QtWidgets.QWidget(SecondMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.plotWidgetImg = mplwidget(self.centralwidget)
        self.plotWidgetImg.setObjectName("plotWidgetImg")
        self.gridLayout_2.addWidget(self.plotWidgetImg, 0, 0, 1, 1)
        SecondMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SecondMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 445, 21))
        self.menubar.setObjectName("menubar")
        SecondMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SecondMainWindow)
        self.statusbar.setObjectName("statusbar")
        SecondMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(SecondMainWindow)
        QtCore.QMetaObject.connectSlotsByName(SecondMainWindow)

    def retranslateUi(self, SecondMainWindow):
        _translate = QtCore.QCoreApplication.translate
        SecondMainWindow.setWindowTitle(_translate("SecondMainWindow", "MainWindow"))

from GUI.mplwidget import mplwidget
