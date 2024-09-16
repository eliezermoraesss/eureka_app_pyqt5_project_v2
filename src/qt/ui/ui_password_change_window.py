# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\password_change_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PasswordChangeWindow(object):
    def setupUi(self, PasswordChangeWindow):
        PasswordChangeWindow.setObjectName("PasswordChangeWindow")
        PasswordChangeWindow.resize(480, 400)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        PasswordChangeWindow.setWindowIcon(icon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PasswordChangeWindow.sizePolicy().hasHeightForWidth())
        PasswordChangeWindow.setSizePolicy(sizePolicy)
        PasswordChangeWindow.setFocusPolicy(QtCore.Qt.NoFocus)
        PasswordChangeWindow.setStyleSheet("* {\n"
"    background-color: #ffffff;\n"
"    font-style: \"Segoe UI\";\n"
"     color: #0B090A;\n"
"}\n"
"\n"
"QLabel {\n"
"    color: #0B090A;\n"
"    font-size: 12px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    background-color: #DFE0E2;\n"
"    padding-left: 15px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #fbba72;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #399918;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #6703c5;\n"
"    color: #EEEEEE;\n"
"}\n"
"")
        self.password_label = QtWidgets.QLabel(PasswordChangeWindow)
        self.password_label.setGeometry(QtCore.QRect(90, 90, 131, 21))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.btn_change_password = QtWidgets.QPushButton(PasswordChangeWindow)
        self.btn_change_password.setGeometry(QtCore.QRect(80, 300, 161, 41))
        self.btn_change_password.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_change_password.setFont(font)
        self.btn_change_password.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btn_change_password.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icon/caixa-de-senha-com-asteriscos.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_change_password.setIcon(icon)
        self.btn_change_password.setIconSize(QtCore.QSize(24, 24))
        self.btn_change_password.setObjectName("btn_change_password")
        self.btn_close = QtWidgets.QPushButton(PasswordChangeWindow)
        self.btn_close.setGeometry(QtCore.QRect(270, 300, 111, 41))
        self.btn_close.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_close.setFont(font)
        self.btn_close.setStyleSheet("QPushButton:hover {\n"
"    background-color: #d60000;\n"
"    color: #EEEEEE\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icon/excluir (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon1)
        self.btn_close.setIconSize(QtCore.QSize(16, 16))
        self.btn_close.setObjectName("btn_close")
        self.window_title_bar = QtWidgets.QWidget(PasswordChangeWindow)
        self.window_title_bar.setGeometry(QtCore.QRect(0, 0, 481, 51))
        self.window_title_bar.setStyleSheet("* {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(186, 24, 27, 255), stop:1 rgba(102, 7, 8, 255));\n"
"}")
        self.window_title_bar.setObjectName("window_title_bar")
        self.window_title_label = QtWidgets.QLabel(self.window_title_bar)
        self.window_title_label.setGeometry(QtCore.QRect(150, 0, 181, 51))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.window_title_label.setFont(font)
        self.window_title_label.setStyleSheet("QLabel {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"    font-size: 22px;\n"
"    font-weight: regular;\n"
"    font-style: \"Segoe UI\";\n"
"}")
        self.window_title_label.setObjectName("window_title_label")
        self.password_confirm_label = QtWidgets.QLabel(PasswordChangeWindow)
        self.password_confirm_label.setGeometry(QtCore.QRect(90, 180, 151, 21))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.password_confirm_label.setFont(font)
        self.password_confirm_label.setObjectName("password_confirm_label")
        self.password_field = QtWidgets.QLineEdit(PasswordChangeWindow)
        self.password_field.setGeometry(QtCore.QRect(80, 120, 301, 41))
        self.password_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.password_field.setFont(font)
        self.password_field.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.password_field.setInputMask("")
        self.password_field.setText("")
        self.password_field.setMaxLength(18)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_field.setCursorPosition(0)
        self.password_field.setClearButtonEnabled(True)
        self.password_field.setObjectName("password_field")
        self.password_confirm_field = QtWidgets.QLineEdit(PasswordChangeWindow)
        self.password_confirm_field.setGeometry(QtCore.QRect(80, 210, 301, 41))
        self.password_confirm_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.password_confirm_field.setFont(font)
        self.password_confirm_field.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.password_confirm_field.setWhatsThis("")
        self.password_confirm_field.setInputMask("")
        self.password_confirm_field.setText("")
        self.password_confirm_field.setMaxLength(10)
        self.password_confirm_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_confirm_field.setClearButtonEnabled(True)
        self.password_confirm_field.setObjectName("password_confirm_field")

        self.retranslateUi(PasswordChangeWindow)
        QtCore.QMetaObject.connectSlotsByName(PasswordChangeWindow)

    def retranslateUi(self, PasswordChangeWindow):
        _translate = QtCore.QCoreApplication.translate
        PasswordChangeWindow.setWindowTitle(_translate("PasswordChangeWindow", "Eureka®"))
        self.password_label.setText(_translate("PasswordChangeWindow", "Digite a nova senha:"))
        self.btn_change_password.setText(_translate("PasswordChangeWindow", " Redefinir senha"))
        self.btn_close.setText(_translate("PasswordChangeWindow", " Cancelar"))
        self.window_title_label.setText(_translate("PasswordChangeWindow", "Redefinir senha"))
        self.password_confirm_label.setText(_translate("PasswordChangeWindow", "Confirme a nova senha:"))
from src.qt.ui import resource_rc