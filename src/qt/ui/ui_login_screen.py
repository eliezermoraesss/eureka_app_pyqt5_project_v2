# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\login_screen.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.setEnabled(True)
        LoginWindow.resize(800, 600)
        LoginWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(LoginWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.sidebar_enaplic = QtWidgets.QWidget(self.centralwidget)
        self.sidebar_enaplic.setGeometry(QtCore.QRect(0, 0, 161, 601))
        self.sidebar_enaplic.setStyleSheet("* {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(186, 24, 27, 255), stop:1 rgba(102, 7, 8, 255));\n"
"}")
        self.sidebar_enaplic.setObjectName("sidebar_enaplic")
        self.logo_enaplic = QtWidgets.QLabel(self.sidebar_enaplic)
        self.logo_enaplic.setGeometry(QtCore.QRect(40, 230, 81, 81))
        self.logo_enaplic.setText("")
        self.logo_enaplic.setPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"))
        self.logo_enaplic.setScaledContents(True)
        self.logo_enaplic.setObjectName("logo_enaplic")
        self.main_area = QtWidgets.QWidget(self.centralwidget)
        self.main_area.setGeometry(QtCore.QRect(161, -1, 641, 601))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_area.sizePolicy().hasHeightForWidth())
        self.main_area.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.main_area.setFont(font)
        self.main_area.setStyleSheet("* {\n"
"    background-color: #ffffff;\n"
"    font-style: \"Segoe UI\";\n"
"     color: #0B090A;\n"
"}\n"
"\n"
"QLabel, QCheckBox {\n"
"    color: #0B090A;\n"
"    font-size: 11px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QLabel#logo-enaplic {\n"
"    margin: 5px 0;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    background-color: #DFE0E2;\n"
"    padding-left: 15px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QDateEdit, QComboBox {\n"
"    background-color: #DFE0E2;\n"
"    border: 1px solid #262626;\n"
"    padding: 5px 10px;\n"
"    border-radius: 10px;\n"
"    height: 20px;\n"
"    font-size: 16px;\n"
"}\n"
"\n"
"QDateEdit::drop-down, QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 30px;\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"    border-top-right-radius: 3px;\n"
"    border-bottom-right-radius: 3px;\n"
"}\n"
"\n"
"QDateEdit::down-arrow, QComboBox::down-arrow {\n"
"    image: url(../resources/images/arrow.png);\n"
"    width: 10px;\n"
"    height: 10px;\n"
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
"    background-color: #e5383b;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #6703c5;\n"
"    color: #EEEEEE;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    border: 1px solid #000000;\n"
"    background-color: #686D76;\n"
"    padding-left: 10px;\n"
"    margin-bottom: 15px;\n"
"}\n"
"\n"
"QTableWidget QHeaderView::section {\n"
"    background-color: #262626;\n"
"    color: #A7A6A6;\n"
"    padding: 5px;\n"
"    height: 18px;\n"
"}\n"
"\n"
"QTableWidget QHeaderView::section:horizontal {\n"
"    border-top: 1px solid #333;\n"
"}\n"
"\n"
"QTableWidget::item {\n"
"    background-color: #363636;\n"
"    color: #fff;\n"
"    font-weight: bold;\n"
"    padding-right: 8px;\n"
"    padding-left: 8px;\n"
"}\n"
"\n"
"QTableWidget::item:selected {\n"
"    background-color: #000000;\n"
"    color: #EEEEEE;\n"
"    font-weight: bold;\n"
"}")
        self.main_area.setObjectName("main_area")
        self.user_field = QtWidgets.QLineEdit(self.main_area)
        self.user_field.setGeometry(QtCore.QRect(190, 150, 221, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user_field.sizePolicy().hasHeightForWidth())
        self.user_field.setSizePolicy(sizePolicy)
        self.user_field.setMinimumSize(QtCore.QSize(221, 41))
        self.user_field.setMaximumSize(QtCore.QSize(221, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.user_field.setFont(font)
        self.user_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.user_field.setInputMask("")
        self.user_field.setText("")
        self.user_field.setMaxLength(15)
        self.user_field.setClearButtonEnabled(True)
        self.user_field.setObjectName("user_field")
        self.password_field = QtWidgets.QLineEdit(self.main_area)
        self.password_field.setGeometry(QtCore.QRect(190, 230, 221, 41))
        self.password_field.setMinimumSize(QtCore.QSize(221, 41))
        self.password_field.setMaximumSize(QtCore.QSize(221, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.password_field.setFont(font)
        self.password_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.password_field.setInputMask("")
        self.password_field.setText("")
        self.password_field.setMaxLength(18)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_field.setClearButtonEnabled(True)
        self.password_field.setObjectName("password_field")
        self.btn_login = QtWidgets.QPushButton(self.main_area)
        self.btn_login.setGeometry(QtCore.QRect(190, 330, 221, 41))
        self.btn_login.setMinimumSize(QtCore.QSize(221, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_login.setFont(font)
        self.btn_login.setStyleSheet("QPushButton:hover {\n"
"    background-color: #399918;\n"
"    color: #EEEEEE;\n"
"    font-style: \"Segoe UI\";\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icon/entrar (2).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_login.setIcon(icon)
        self.btn_login.setIconSize(QtCore.QSize(24, 24))
        self.btn_login.setObjectName("btn_login")
        self.btn_register = QtWidgets.QPushButton(self.main_area)
        self.btn_register.setGeometry(QtCore.QRect(190, 390, 221, 41))
        self.btn_register.setMinimumSize(QtCore.QSize(221, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_register.setFont(font)
        self.btn_register.setStyleSheet("QPushButton:hover {\n"
"    background-color: #00b4d8;\n"
"    color: #EEEEEE\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icon/add-user-64.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_register.setIcon(icon1)
        self.btn_register.setIconSize(QtCore.QSize(24, 24))
        self.btn_register.setObjectName("btn_register")
        self.btn_forget_password = QtWidgets.QPushButton(self.main_area)
        self.btn_forget_password.setGeometry(QtCore.QRect(190, 450, 221, 41))
        self.btn_forget_password.setMinimumSize(QtCore.QSize(221, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_forget_password.setFont(font)
        self.btn_forget_password.setStyleSheet("QPushButton:hover {\n"
"    background-color: #ff6700;\n"
"    color: #EEEEEE\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/icon/cadeado (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_forget_password.setIcon(icon2)
        self.btn_forget_password.setIconSize(QtCore.QSize(24, 24))
        self.btn_forget_password.setObjectName("btn_forget_password")
        self.user_label = QtWidgets.QLabel(self.main_area)
        self.user_label.setGeometry(QtCore.QRect(200, 130, 47, 13))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.user_label.setFont(font)
        self.user_label.setObjectName("user_label")
        self.password_label = QtWidgets.QLabel(self.main_area)
        self.password_label.setGeometry(QtCore.QRect(200, 210, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.logo_enaplic_50 = QtWidgets.QLabel(self.main_area)
        self.logo_enaplic_50.setGeometry(QtCore.QRect(500, 490, 121, 101))
        self.logo_enaplic_50.setText("")
        self.logo_enaplic_50.setPixmap(QtGui.QPixmap(":/image/image/logo_enaplic_50_anos.png"))
        self.logo_enaplic_50.setScaledContents(True)
        self.logo_enaplic_50.setObjectName("logo_enaplic_50")
        self.btn_close = QtWidgets.QPushButton(self.main_area)
        self.btn_close.setGeometry(QtCore.QRect(600, 0, 31, 41))
        self.btn_close.setMinimumSize(QtCore.QSize(0, 41))
        self.btn_close.setStyleSheet("* {\n"
"    background-color: #FFF;\n"
"}")
        self.btn_close.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/icon/excluir.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon3)
        self.btn_close.setIconSize(QtCore.QSize(24, 24))
        self.btn_close.setObjectName("btn_close")
        self.window_title_label = QtWidgets.QLabel(self.main_area)
        self.window_title_label.setGeometry(QtCore.QRect(110, 10, 401, 61))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.window_title_label.setFont(font)
        self.window_title_label.setStyleSheet("QLabel {\n"
"    background-color: transparent;\n"
"    color: #a4161a;\n"
"    font-size: 28px;\n"
"    font-weight: bold;\n"
"    font-style: \"Segoe UI\";\n"
"}")
        self.window_title_label.setObjectName("window_title_label")
        LoginWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "MainWindow"))
        self.btn_login.setText(_translate("LoginWindow", " Acessar"))
        self.btn_register.setText(_translate("LoginWindow", " Cadastrar usuário"))
        self.btn_forget_password.setText(_translate("LoginWindow", " Esqueci minha senha"))
        self.user_label.setText(_translate("LoginWindow", "Usuário"))
        self.password_label.setText(_translate("LoginWindow", "Senha"))
        self.window_title_label.setText(_translate("LoginWindow", "Seja bem-vindo(a) ao Eureka®"))
from src.qt.ui import resource_rc