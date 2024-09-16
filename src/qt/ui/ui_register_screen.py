# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\register_screen.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RegisterWindow(object):
    def setupUi(self, RegisterWindow):
        RegisterWindow.setObjectName("RegisterWindow")
        RegisterWindow.setEnabled(True)
        RegisterWindow.resize(800, 600)
        RegisterWindow.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        RegisterWindow.setWindowIcon(icon)
        self.central_widget = QtWidgets.QWidget(RegisterWindow)
        self.central_widget.setObjectName("central_widget")
        self.window_title_bar = QtWidgets.QWidget(self.central_widget)
        self.window_title_bar.setGeometry(QtCore.QRect(160, 0, 641, 51))
        self.window_title_bar.setStyleSheet("* {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(102, 7, 8, 255), stop:1 rgba(102, 7, 8, 255));\n"
"}")
        self.window_title_bar.setObjectName("window_title_bar")
        self.window_title_label = QtWidgets.QLabel(self.window_title_bar)
        self.window_title_label.setGeometry(QtCore.QRect(140, -5, 321, 51))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.window_title_label.setFont(font)
        self.window_title_label.setStyleSheet("QLabel {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"    font-size: 28px;\n"
"    font-weight: regular;\n"
"    font-style: \"Segoe UI\";\n"
"}")
        self.window_title_label.setObjectName("window_title_label")
        self.main_area = QtWidgets.QWidget(self.central_widget)
        self.main_area.setGeometry(QtCore.QRect(159, 49, 641, 601))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_area.sizePolicy().hasHeightForWidth())
        self.main_area.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.main_area.setFont(font)
        self.main_area.setToolTipDuration(-4)
        self.main_area.setStyleSheet("* {\n"
"    background-color: #ffffff;\n"
"    font-style: \'Segoe UI\';\n"
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
"    padding: 5px 10px;\n"
"    border-radius: 18px;\n"
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
"    image: url(../static/icon/arrow.png);\n"
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

        self.name_field = QtWidgets.QLineEdit(self.main_area)
        self.user_field = QtWidgets.QLineEdit(self.main_area)
        self.email_field = QtWidgets.QLineEdit(self.main_area)
        self.password_field = QtWidgets.QLineEdit(self.main_area)
        self.area_combobox_field = QtWidgets.QComboBox(self.main_area)
        self.btn_save = QtWidgets.QPushButton(self.main_area)
        self.btn_close = QtWidgets.QPushButton(self.main_area)

        self.user_field.setGeometry(QtCore.QRect(150, 140, 301, 41))
        self.user_field.setMinimumSize(QtCore.QSize(301, 41))
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
        self.email_field.setGeometry(QtCore.QRect(150, 220, 301, 41))
        self.email_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.email_field.setFont(font)
        self.email_field.setTabletTracking(False)
        self.email_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.email_field.setInputMask("")
        self.email_field.setText("")
        self.email_field.setMaxLength(30)
        self.email_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.email_field.setClearButtonEnabled(True)
        self.email_field.setObjectName("email_field")
        self.user_label = QtWidgets.QLabel(self.main_area)
        self.user_label.setGeometry(QtCore.QRect(160, 120, 47, 13))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.user_label.setFont(font)
        self.user_label.setObjectName("user_label")
        self.email_label = QtWidgets.QLabel(self.main_area)
        self.email_label.setGeometry(QtCore.QRect(160, 200, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.email_label.setFont(font)
        self.email_label.setObjectName("email_label")

        self.btn_close.setGeometry(QtCore.QRect(310, 460, 91, 41))
        self.btn_close.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_close.setFont(font)
        self.btn_close.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_close.setStyleSheet("QPushButton:hover {\n"
"    background-color: #d60000;\n"
"    color: #EEEEEE\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icon/arrow-92-64.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon)
        self.btn_close.setIconSize(QtCore.QSize(16, 16))
        self.btn_close.setObjectName("btn_close")
        self.name_label = QtWidgets.QLabel(self.main_area)
        self.name_label.setGeometry(QtCore.QRect(160, 40, 47, 13))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.name_field.setGeometry(QtCore.QRect(150, 60, 301, 41))
        self.name_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.name_field.setFont(font)
        self.name_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.name_field.setAccessibleDescription("")
        self.name_field.setInputMask("")
        self.name_field.setText("")
        self.name_field.setMaxLength(30)
        self.name_field.setClearButtonEnabled(True)
        self.name_field.setObjectName("name_field")
        self.password_field.setGeometry(QtCore.QRect(150, 300, 301, 41))
        self.password_field.setMinimumSize(QtCore.QSize(301, 41))
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
        self.password_label = QtWidgets.QLabel(self.main_area)
        self.password_label.setGeometry(QtCore.QRect(160, 280, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.area_combobox_field.setGeometry(QtCore.QRect(150, 380, 301, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.area_combobox_field.sizePolicy().hasHeightForWidth())
        self.area_combobox_field.setSizePolicy(sizePolicy)
        self.area_combobox_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.area_combobox_field.setFont(font)
        self.area_combobox_field.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.area_combobox_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.area_combobox_field.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.area_combobox_field.setIconSize(QtCore.QSize(32, 32))
        self.area_combobox_field.setObjectName("area_combobox_field")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.setItemText(0, "")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_combobox_field.addItem("")
        self.area_lable = QtWidgets.QLabel(self.main_area)
        self.area_lable.setGeometry(QtCore.QRect(160, 360, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.area_lable.setFont(font)
        self.area_lable.setObjectName("area_lable")
        self.icon_name_label = QtWidgets.QLabel(self.main_area)
        self.icon_name_label.setGeometry(QtCore.QRect(100, 60, 32, 32))
        self.icon_name_label.setText("")
        self.icon_name_label.setPixmap(QtGui.QPixmap(":/icon/icon/user-64.ico"))
        self.icon_name_label.setScaledContents(True)
        self.icon_name_label.setObjectName("icon_name_label")
        self.icon_user_label = QtWidgets.QLabel(self.main_area)
        self.icon_user_label.setGeometry(QtCore.QRect(100, 140, 32, 32))
        self.icon_user_label.setText("")
        self.icon_user_label.setPixmap(QtGui.QPixmap(":/icon/icon/user-3-64.ico"))
        self.icon_user_label.setScaledContents(True)
        self.icon_user_label.setObjectName("icon_user_label")
        self.icon_email_label = QtWidgets.QLabel(self.main_area)
        self.icon_email_label.setGeometry(QtCore.QRect(100, 220, 32, 32))
        self.icon_email_label.setText("")
        self.icon_email_label.setPixmap(QtGui.QPixmap(":/icon/icon/no.png"))
        self.icon_email_label.setScaledContents(True)
        self.icon_email_label.setObjectName("icon_email_label")
        self.icon_password_label = QtWidgets.QLabel(self.main_area)
        self.icon_password_label.setGeometry(QtCore.QRect(100, 300, 32, 32))
        self.icon_password_label.setText("")
        self.icon_password_label.setPixmap(QtGui.QPixmap(":/icon/icon/cadeado (1).png"))
        self.icon_password_label.setScaledContents(True)
        self.icon_password_label.setObjectName("icon_password_label")
        self.icon_area_label = QtWidgets.QLabel(self.main_area)
        self.icon_area_label.setGeometry(QtCore.QRect(100, 380, 32, 32))
        self.icon_area_label.setText("")
        self.icon_area_label.setPixmap(QtGui.QPixmap(":/icon/icon/factory-2-64.ico"))
        self.icon_area_label.setScaledContents(True)
        self.icon_area_label.setObjectName("icon_area_label")
        self.logo_enaplic_50 = QtWidgets.QLabel(self.main_area)
        self.logo_enaplic_50.setGeometry(QtCore.QRect(500, 440, 121, 101))
        self.logo_enaplic_50.setText("")
        self.logo_enaplic_50.setPixmap(QtGui.QPixmap(":/image/image/logo_enaplic_50_anos.png"))
        self.logo_enaplic_50.setScaledContents(True)
        self.logo_enaplic_50.setObjectName("logo_enaplic_50")
        self.btn_save.setGeometry(QtCore.QRect(200, 460, 91, 41))
        self.btn_save.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        self.btn_save.setFont(font)
        self.btn_save.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_save.setStyleSheet("QPushButton:hover {\n"
"    background-color: #399918;\n"
"    color: #EEEEEE\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icon/icons8-salvar-50.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_save.setIcon(icon1)
        self.btn_save.setIconSize(QtCore.QSize(16, 16))
        self.btn_save.setObjectName("btn_save")
        self.sidebar_enaplic = QtWidgets.QWidget(self.central_widget)
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
        RegisterWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(RegisterWindow)
        QtCore.QMetaObject.connectSlotsByName(RegisterWindow)

    def retranslateUi(self, RegisterWindow):
        _translate = QtCore.QCoreApplication.translate
        RegisterWindow.setWindowTitle(_translate("RegisterWindow", "MainWindow"))
        self.window_title_label.setText(_translate("RegisterWindow", "Cadastro de novo usuário"))
        self.user_label.setText(_translate("RegisterWindow", "Usuário"))
        self.email_label.setText(_translate("RegisterWindow", "E-mail"))
        self.btn_close.setText(_translate("RegisterWindow", " Voltar"))
        self.name_label.setText(_translate("RegisterWindow", "Nome"))
        self.password_label.setText(_translate("RegisterWindow", "Senha"))
        self.area_combobox_field.setItemText(1, _translate("RegisterWindow", "Almoxarifado"))
        self.area_combobox_field.setItemText(2, _translate("RegisterWindow", "Comercial"))
        self.area_combobox_field.setItemText(3, _translate("RegisterWindow", "Compras"))
        self.area_combobox_field.setItemText(4, _translate("RegisterWindow", "Elétrica"))
        self.area_combobox_field.setItemText(5, _translate("RegisterWindow", "Engenharia"))
        self.area_combobox_field.setItemText(6, _translate("RegisterWindow", "Expedição"))
        self.area_combobox_field.setItemText(7, _translate("RegisterWindow", "Fiscal"))
        self.area_combobox_field.setItemText(8, _translate("RegisterWindow", "PCP"))
        self.area_combobox_field.setItemText(9, _translate("RegisterWindow", "RH"))
        self.area_lable.setText(_translate("RegisterWindow", "Setor"))
        self.btn_save.setText(_translate("RegisterWindow", " Salvar"))
from src.qt.ui import resource_rc