# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\edit_product_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator


class Ui_EditProductWindow(object):
    def setupUi(self, EditProductWindow):
        EditProductWindow.setObjectName("EditProductWindow")
        EditProductWindow.resize(640, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EditProductWindow.setWindowIcon(icon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EditProductWindow.sizePolicy().hasHeightForWidth())
        EditProductWindow.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EditProductWindow.setWindowIcon(icon)
        EditProductWindow.setStyleSheet("* {\n"
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
"    font-size: 18px;\n"
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
        self.window_title_bar = QtWidgets.QWidget(EditProductWindow)
        self.window_title_bar.setGeometry(QtCore.QRect(0, 0, 641, 51))
        self.window_title_bar.setStyleSheet("* {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(186, 24, 27, 255), stop:1 rgba(102, 7, 8, 255));\n"
"}")
        self.window_title_bar.setObjectName("window_title_bar")
        self.type_label = QtWidgets.QLabel(self.window_title_bar)
        self.type_label.setGeometry(QtCore.QRect(50, 0, 261, 51))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.type_label.setFont(font)
        self.type_label.setStyleSheet("QLabel {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"    font-size: 22px;\n"
"    font-weight: regular;\n"
"    font-style: \"Segoe UI\";\n"
"}")
        self.type_label.setObjectName("type_label")
        self.enaplic_logo = QtWidgets.QLabel(self.window_title_bar)
        self.enaplic_logo.setGeometry(QtCore.QRect(590, 4, 41, 41))
        self.enaplic_logo.setText("")
        self.enaplic_logo.setPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"))
        self.enaplic_logo.setScaledContents(True)
        self.enaplic_logo.setObjectName("enaplic_logo")
        self.main_area = QtWidgets.QWidget(EditProductWindow)
        self.main_area.setGeometry(QtCore.QRect(0, 50, 641, 551))
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
"    padding-left: 11px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QDateEdit, QComboBox {\n"
"    background-color: #DFE0E2;\n"
"    padding-left: 11px;\n"
"    border-radius: 18px;\n"
"    height: 20px;\n"
"    font-size: 14px;\n"
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

        self.descricao_field = QtWidgets.QLineEdit(self.main_area)
        self.desc_comp_field = QtWidgets.QLineEdit(self.main_area)
        self.tipo_field = QtWidgets.QLineEdit(self.main_area)
        self.btn_search_tipo = QtWidgets.QPushButton(self.main_area)
        self.um_field = QtWidgets.QLineEdit(self.main_area)
        self.btn_search_um = QtWidgets.QPushButton(self.main_area)
        self.armazem_field = QtWidgets.QLineEdit(self.main_area)
        self.btn_search_arm = QtWidgets.QPushButton(self.main_area)
        self.cc_field = QtWidgets.QLineEdit(self.main_area)
        self.btn_search_cc = QtWidgets.QPushButton(self.main_area)
        self.bloquear_combobox = QtWidgets.QComboBox(self.main_area)
        self.endereco_field = QtWidgets.QLineEdit(self.main_area)
        self.grupo_field = QtWidgets.QLineEdit(self.main_area)
        self.btn_search_grupo = QtWidgets.QPushButton(self.main_area)
        self.desc_grupo_field = QtWidgets.QLineEdit(self.main_area)
        self.ncm_field = QtWidgets.QLineEdit(self.main_area)
        self.peso_field = QtWidgets.QLineEdit(self.main_area)

        self.btn_save = QtWidgets.QPushButton(self.main_area)
        self.btn_close = QtWidgets.QPushButton(self.main_area)

        self.desc_comp_field.setGeometry(QtCore.QRect(50, 120, 551, 41))
        self.desc_comp_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.desc_comp_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.desc_comp_field.setFont(font)
        self.desc_comp_field.setInputMask("")
        self.desc_comp_field.setText("")
        self.desc_comp_field.setMaxLength(60)
        self.desc_comp_field.setClearButtonEnabled(True)
        self.desc_comp_field.setObjectName("desc_comp_field")

        self.tipo_field.setGeometry(QtCore.QRect(50, 200, 91, 41))
        self.tipo_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.tipo_field.setFont(font)
        self.tipo_field.setTabletTracking(False)
        self.tipo_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tipo_field.setInputMask("")
        self.tipo_field.setText("")
        self.tipo_field.setMaxLength(2)
        self.tipo_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.tipo_field.setClearButtonEnabled(True)
        self.tipo_field.setObjectName("tipo_field")

        self.desc_comp_label = QtWidgets.QLabel(self.main_area)
        self.desc_comp_label.setGeometry(QtCore.QRect(60, 100, 131, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.desc_comp_label.setFont(font)
        self.desc_comp_label.setObjectName("desc_comp_label")

        self.tipo_label = QtWidgets.QLabel(self.main_area)
        self.tipo_label.setGeometry(QtCore.QRect(60, 180, 51, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.tipo_label.setFont(font)
        self.tipo_label.setObjectName("tipo_label")

        self.btn_close.setGeometry(QtCore.QRect(490, 480, 111, 41))
        self.btn_close.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_close.setFont(font)
        self.btn_close.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_close.setStyleSheet("QPushButton {\n"
"    background-color: #fbba72;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #d60000;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #6703c5;\n"
"    color: #EEEEEE;\n"
"}\n"
"\n"
"")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icon/excluir (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon1)
        self.btn_close.setIconSize(QtCore.QSize(16, 16))
        self.btn_close.setObjectName("btn_close")

        self.descricao_label = QtWidgets.QLabel(self.main_area)
        self.descricao_label.setGeometry(QtCore.QRect(60, 20, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.descricao_label.setFont(font)
        self.descricao_label.setObjectName("descricao_label")

        self.descricao_field.setGeometry(QtCore.QRect(50, 40, 551, 41))
        self.descricao_field.setMinimumSize(QtCore.QSize(301, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.descricao_field.setFont(font)
        self.descricao_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.descricao_field.setAccessibleDescription("")
        self.descricao_field.setInputMask("")
        self.descricao_field.setText("")
        self.descricao_field.setMaxLength(100)
        self.descricao_field.setClearButtonEnabled(True)
        self.descricao_field.setObjectName("descricao_field")

        self.um_field.setGeometry(QtCore.QRect(220, 200, 91, 41))
        self.um_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.um_field.setFont(font)
        self.um_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.um_field.setInputMask("")
        self.um_field.setText("")
        self.um_field.setMaxLength(2)
        self.um_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.um_field.setClearButtonEnabled(True)
        self.um_field.setObjectName("um_field")

        self.um_label = QtWidgets.QLabel(self.main_area)
        self.um_label.setGeometry(QtCore.QRect(230, 180, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.um_label.setFont(font)
        self.um_label.setObjectName("um_label")

        self.armazem_label = QtWidgets.QLabel(self.main_area)
        self.armazem_label.setGeometry(QtCore.QRect(390, 180, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.armazem_label.setFont(font)
        self.armazem_label.setObjectName("armazem_label")

        self.btn_save.setGeometry(QtCore.QRect(360, 480, 111, 41))
        self.btn_save.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_save.setFont(font)
        self.btn_save.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_save.setStyleSheet("QPushButton {\n"
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
"QPushButton:pressed {\n"
"    background-color: #6703c5;\n"
"    color: #EEEEEE;\n"
"}\n"
"\n"
"")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/icon/icons8-salvar-50.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_save.setIcon(icon2)
        self.btn_save.setIconSize(QtCore.QSize(16, 16))
        self.btn_save.setObjectName("btn_save")

        self.grupo_field.setGeometry(QtCore.QRect(50, 360, 91, 41))
        self.grupo_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.grupo_field.setFont(font)
        self.grupo_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.grupo_field.setInputMask("")
        self.grupo_field.setText("")
        self.grupo_field.setMaxLength(4)
        self.grupo_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.grupo_field.setClearButtonEnabled(True)
        self.grupo_field.setObjectName("grupo_field")

        self.grupo_label = QtWidgets.QLabel(self.main_area)
        self.grupo_label.setGeometry(QtCore.QRect(60, 340, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.grupo_label.setFont(font)
        self.grupo_label.setObjectName("grupo_label")

        self.desc_grupo_field.setGeometry(QtCore.QRect(210, 360, 391, 41))
        self.desc_grupo_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.desc_grupo_field.setFont(font)
        self.desc_grupo_field.setFocusPolicy(QtCore.Qt.NoFocus)
        self.desc_grupo_field.setInputMask("")
        self.desc_grupo_field.setText("")
        self.desc_grupo_field.setMaxLength(30)
        self.desc_grupo_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.desc_grupo_field.setReadOnly(True)
        self.desc_grupo_field.setClearButtonEnabled(False)
        self.desc_grupo_field.setObjectName("desc_grupo_field")

        self.ncm_field.setGeometry(QtCore.QRect(50, 440, 131, 41))
        self.ncm_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.ncm_field.setFont(font)
        self.ncm_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.ncm_field.setInputMask("")
        self.ncm_field.setText("")
        self.ncm_field.setMaxLength(8)
        self.ncm_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.ncm_field.setClearButtonEnabled(True)
        self.ncm_field.setObjectName("ncm_field")

        self.peso_field.setGeometry(QtCore.QRect(210, 440, 151, 41))
        self.peso_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.peso_field.setFont(font)
        self.peso_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.peso_field.setInputMask("")
        self.peso_field.setText("")
        self.peso_field.setMaxLength(9)
        self.peso_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.peso_field.setClearButtonEnabled(True)
        self.peso_field.setObjectName("peso_field")

        # Adicionando o validador para aceitar apenas valores decimais com vírgula
        decimal_regex = QRegExp(r'^\d{0,7},\d{0,4}$')
        validator = QRegExpValidator(decimal_regex)
        self.peso_field.setValidator(validator)

        self.ncm_label = QtWidgets.QLabel(self.main_area)
        self.ncm_label.setGeometry(QtCore.QRect(60, 420, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.ncm_label.setFont(font)
        self.ncm_label.setObjectName("ncm_label")

        self.peso_label = QtWidgets.QLabel(self.main_area)
        self.peso_label.setGeometry(QtCore.QRect(220, 420, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.peso_label.setFont(font)
        self.peso_label.setObjectName("peso_label")

        self.desc_grupo_label = QtWidgets.QLabel(self.main_area)
        self.desc_grupo_label.setGeometry(QtCore.QRect(210, 340, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.desc_grupo_label.setFont(font)
        self.desc_grupo_label.setObjectName("desc_grupo_label")

        self.cc_label = QtWidgets.QLabel(self.main_area)
        self.cc_label.setGeometry(QtCore.QRect(60, 260, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.cc_label.setFont(font)
        self.cc_label.setObjectName("cc_label")

        self.bloquear_combobox.setGeometry(QtCore.QRect(240, 280, 101, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bloquear_combobox.sizePolicy().hasHeightForWidth())
        self.bloquear_combobox.setSizePolicy(sizePolicy)
        self.bloquear_combobox.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.bloquear_combobox.setFont(font)
        self.bloquear_combobox.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.bloquear_combobox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.bloquear_combobox.setMaxCount(10)
        self.bloquear_combobox.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.bloquear_combobox.setIconSize(QtCore.QSize(32, 32))
        self.bloquear_combobox.setObjectName("bloquear_combobox")
        self.bloquear_combobox.addItem("")
        self.bloquear_combobox.addItem("")

        self.bloquear_label = QtWidgets.QLabel(self.main_area)
        self.bloquear_label.setGeometry(QtCore.QRect(250, 260, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.bloquear_label.setFont(font)
        self.bloquear_label.setObjectName("bloquear_label")

        self.endereco_field.setGeometry(QtCore.QRect(380, 280, 221, 41))
        self.endereco_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.endereco_field.setFont(font)
        self.endereco_field.setTabletTracking(False)
        self.endereco_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.endereco_field.setInputMask("")
        self.endereco_field.setText("")
        self.endereco_field.setMaxLength(6)
        self.endereco_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.endereco_field.setClearButtonEnabled(True)
        self.endereco_field.setObjectName("endereco_field")

        self.endereco_label = QtWidgets.QLabel(self.main_area)
        self.endereco_label.setGeometry(QtCore.QRect(390, 260, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.endereco_label.setFont(font)
        self.endereco_label.setObjectName("endereco_label")

        self.armazem_field.setGeometry(QtCore.QRect(380, 200, 91, 41))
        self.armazem_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.armazem_field.setFont(font)
        self.armazem_field.setTabletTracking(False)
        self.armazem_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.armazem_field.setInputMask("")
        self.armazem_field.setText("")
        self.armazem_field.setMaxLength(6)
        self.armazem_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.armazem_field.setClearButtonEnabled(True)
        self.armazem_field.setObjectName("armazem_field")

        self.cc_field.setGeometry(QtCore.QRect(50, 280, 121, 41))
        self.cc_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.cc_field.setFont(font)
        self.cc_field.setTabletTracking(False)
        self.cc_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.cc_field.setInputMask("")
        self.cc_field.setText("")
        self.cc_field.setMaxLength(9)
        self.cc_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.cc_field.setClearButtonEnabled(True)
        self.cc_field.setObjectName("cc_field")

        self.btn_search_tipo.setGeometry(QtCore.QRect(145, 200, 41, 41))
        self.btn_search_tipo.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_search_tipo.setFont(font)
        self.btn_search_tipo.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_search_tipo.setStyleSheet("QPushButton {\n"
"    background-color: #fff;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"}")
        self.btn_search_tipo.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/icon/lupa (2).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_search_tipo.setIcon(icon3)
        self.btn_search_tipo.setIconSize(QtCore.QSize(32, 32))
        self.btn_search_tipo.setObjectName("btn_search_tipo")

        self.btn_search_um.setGeometry(QtCore.QRect(315, 200, 41, 41))
        self.btn_search_um.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_search_um.setFont(font)
        self.btn_search_um.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_search_um.setStyleSheet("QPushButton {\n"
"    background-color: #fff;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"}")
        self.btn_search_um.setText("")
        self.btn_search_um.setIcon(icon3)
        self.btn_search_um.setIconSize(QtCore.QSize(32, 32))
        self.btn_search_um.setObjectName("btn_search_um")

        self.btn_search_arm.setGeometry(QtCore.QRect(475, 200, 41, 41))
        self.btn_search_arm.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_search_arm.setFont(font)
        self.btn_search_arm.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_search_arm.setStyleSheet("QPushButton {\n"
"    background-color: #fff;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"}")
        self.btn_search_arm.setText("")
        self.btn_search_arm.setIcon(icon3)
        self.btn_search_arm.setIconSize(QtCore.QSize(32, 32))
        self.btn_search_arm.setObjectName("btn_search_arm")

        self.btn_search_cc.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_search_cc.setGeometry(QtCore.QRect(175, 280, 41, 41))
        self.btn_search_cc.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_search_cc.setFont(font)
        self.btn_search_cc.setStyleSheet("QPushButton {\n"
"    background-color: #fff;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"}")
        self.btn_search_cc.setText("")
        self.btn_search_cc.setIcon(icon3)
        self.btn_search_cc.setIconSize(QtCore.QSize(32, 32))
        self.btn_search_cc.setObjectName("btn_search_cc")

        self.btn_search_grupo.setGeometry(QtCore.QRect(145, 360, 41, 41))
        self.btn_search_grupo.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_search_grupo.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(1)
        self.btn_search_grupo.setFont(font)
        self.btn_search_grupo.setStyleSheet("QPushButton {\n"
"    background-color: #fff;\n"
"    border: 2px;\n"
"    border-radius: 18px;\n"
"    font-size: 14px;\n"
"    font-weight: regular;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: transparent;\n"
"    color: #EEEEEE;\n"
"}")
        self.btn_search_grupo.setText("")
        self.btn_search_grupo.setIcon(icon3)
        self.btn_search_grupo.setIconSize(QtCore.QSize(32, 32))
        self.btn_search_grupo.setObjectName("btn_search_grupo")

        self.logo_enaplic_50 = QtWidgets.QLabel(self.main_area)
        self.logo_enaplic_50.setGeometry(QtCore.QRect(50, 450, 121, 101))
        self.logo_enaplic_50.setText("")
        self.logo_enaplic_50.setPixmap(QtGui.QPixmap(":/image/image/logo_enaplic_50_anos.png"))
        self.logo_enaplic_50.setScaledContents(True)
        self.logo_enaplic_50.setObjectName("logo_enaplic_50")

        self.retranslateUi(EditProductWindow)
        QtCore.QMetaObject.connectSlotsByName(EditProductWindow)

    def retranslateUi(self, EditProductWindow):
        _translate = QtCore.QCoreApplication.translate
        EditProductWindow.setWindowTitle(_translate("EditProductWindow", "Alterar produto"))
        self.type_label.setText(_translate("EditProductWindow", "{part_number}"))
        self.desc_comp_label.setText(_translate("EditProductWindow", "Desc. Complementar"))
        self.tipo_label.setText(_translate("EditProductWindow", "Tipo"))
        self.btn_close.setText(_translate("EditProductWindow", " Cancelar"))
        self.descricao_label.setText(_translate("EditProductWindow", "Descrição"))
        self.um_label.setText(_translate("EditProductWindow", "Unid. Medida"))
        self.armazem_label.setText(_translate("EditProductWindow", "Armazém"))
        self.btn_save.setText(_translate("EditProductWindow", " Salvar"))
        self.grupo_label.setText(_translate("EditProductWindow", "Grupo"))
        self.desc_grupo_label.setText(_translate("EditProductWindow", "Descrição Grupo"))
        self.cc_label.setText(_translate("EditProductWindow", "Centro de Custo"))
        self.bloquear_combobox.setItemText(0, _translate("EditProductWindow", "Não"))
        self.bloquear_combobox.setItemText(1, _translate("EditProductWindow", "Sim"))
        self.bloquear_label.setText(_translate("EditProductWindow", "Bloquear?"))
        self.endereco_label.setText(_translate("EditProductWindow", "Endereço estoque"))
        self.ncm_label.setText(_translate("EditProductWindow", "NCM"))
        self.peso_label.setText(_translate("EditProductWindow", "Peso Líquido"))
from src.qt.ui import resource_rc
