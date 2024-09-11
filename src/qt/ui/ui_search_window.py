# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\search_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SearchWindow(object):
    def setupUi(self, SearchWindow):
        SearchWindow.setObjectName("SearchWindow")
        SearchWindow.resize(640, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SearchWindow.sizePolicy().hasHeightForWidth())
        SearchWindow.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/image/LOGO.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SearchWindow.setWindowIcon(icon)
        SearchWindow.setStyleSheet("* {\n"
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
        self.window_title_bar = QtWidgets.QWidget(SearchWindow)
        self.window_title_bar.setGeometry(QtCore.QRect(0, 0, 641, 51))
        self.window_title_bar.setStyleSheet("* {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(186, 24, 27, 255), stop:1 rgba(102, 7, 8, 255));\n"
"}")
        self.window_title_bar.setObjectName("window_title_bar")
        self.type_label = QtWidgets.QLabel(self.window_title_bar)
        self.type_label.setGeometry(QtCore.QRect(30, 0, 421, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
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
        self.main_area = QtWidgets.QWidget(SearchWindow)
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
"QLabel {\n"
"    color: #0B090A;\n"
"    font-size: 11px;\n"
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
"QComboBox {\n"
"    background-color: #DFE0E2;\n"
"    padding: 5px 10px;\n"
"    border-radius: 18px;\n"
"    height: 20px;\n"
"    font-size: 16px;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
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
"QComboBox::down-arrow {\n"
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
"}")
        self.main_area.setObjectName("main_area")
        self.btn_close = QtWidgets.QPushButton(self.main_area)
        self.btn_close.setGeometry(QtCore.QRect(510, 480, 111, 41))
        self.btn_close.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.btn_close.setFont(font)
        self.btn_close.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btn_close.setStyleSheet("QPushButton:hover {\n"
"    background-color: #d60000;\n"
"    color: #EEEEEE\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/icon/excluir (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon1)
        self.btn_close.setIconSize(QtCore.QSize(16, 16))
        self.btn_close.setObjectName("btn_close")
        self.search_label = QtWidgets.QLabel(self.main_area)
        self.search_label.setGeometry(QtCore.QRect(30, 10, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.search_label.setFont(font)
        self.search_label.setObjectName("search_label")
        self.search_field = QtWidgets.QLineEdit(self.main_area)
        self.search_field.setGeometry(QtCore.QRect(20, 30, 321, 41))
        self.search_field.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.search_field.setFont(font)
        self.search_field.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.search_field.setAccessibleDescription("")
        self.search_field.setStyleSheet("")
        self.search_field.setInputMask("")
        self.search_field.setText("")
        self.search_field.setMaxLength(100)
        self.search_field.setClearButtonEnabled(True)
        self.search_field.setObjectName("search_field")
        self.btn_ok = QtWidgets.QPushButton(self.main_area)
        self.btn_ok.setGeometry(QtCore.QRect(380, 480, 111, 41))
        self.btn_ok.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.btn_ok.setFont(font)
        self.btn_ok.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btn_ok.setStyleSheet("QPushButton:hover {\n"
"    background-color: #399918;\n"
"    color: #EEEEEE\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/icon/carraca.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_ok.setIcon(icon2)
        self.btn_ok.setIconSize(QtCore.QSize(16, 16))
        self.btn_ok.setObjectName("btn_ok")
        self.type_search_combobox = QtWidgets.QComboBox(self.main_area)
        self.type_search_combobox.setGeometry(QtCore.QRect(420, 30, 201, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.type_search_combobox.sizePolicy().hasHeightForWidth())
        self.type_search_combobox.setSizePolicy(sizePolicy)
        self.type_search_combobox.setMinimumSize(QtCore.QSize(10, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.type_search_combobox.setFont(font)
        self.type_search_combobox.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.type_search_combobox.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.type_search_combobox.setMaxVisibleItems(10)
        self.type_search_combobox.setMaxCount(10)
        self.type_search_combobox.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.type_search_combobox.setIconSize(QtCore.QSize(32, 32))
        self.type_search_combobox.setModelColumn(0)
        self.type_search_combobox.setObjectName("type_search_combobox")
        self.type_search_combobox.addItem("")
        self.type_search_combobox.addItem("")
        self.type_search_label = QtWidgets.QLabel(self.main_area)
        self.type_search_label.setGeometry(QtCore.QRect(430, 10, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.type_search_label.setFont(font)
        self.type_search_label.setObjectName("type_search_label")
        self.btn_search = QtWidgets.QPushButton(self.main_area)
        self.btn_search.setGeometry(QtCore.QRect(345, 30, 41, 41))
        self.btn_search.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.btn_search.setFont(font)
        self.btn_search.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btn_search.setStyleSheet("QPushButton {\n"
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
        self.btn_search.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/icon/lupa (2).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_search.setIcon(icon3)
        self.btn_search.setIconSize(QtCore.QSize(32, 32))
        self.btn_search.setObjectName("btn_search")
        self.search_table = QtWidgets.QTableWidget(self.main_area)
        self.search_table.setGeometry(QtCore.QRect(20, 90, 601, 361))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_table.sizePolicy().hasHeightForWidth())
        self.search_table.setSizePolicy(sizePolicy)
        self.search_table.setStyleSheet("")
        self.search_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.search_table.setAlternatingRowColors(True)
        self.search_table.setShowGrid(False)
        self.search_table.setCornerButtonEnabled(False)
        self.search_table.setRowCount(0)
        self.search_table.setObjectName("search_table")
        self.search_table.setColumnCount(0)
        self.search_table.horizontalHeader().setMinimumSectionSize(100)
        self.search_table.horizontalHeader().setSortIndicatorShown(True)
        self.search_table.horizontalHeader().setStretchLastSection(False)
        self.search_table.verticalHeader().setDefaultSectionSize(25)
        self.search_table.verticalHeader().setMinimumSectionSize(25)
        self.search_table.raise_()
        self.btn_close.raise_()
        self.search_label.raise_()
        self.search_field.raise_()
        self.btn_ok.raise_()
        self.type_search_combobox.raise_()
        self.type_search_label.raise_()
        self.btn_search.raise_()

        self.retranslateUi(SearchWindow)
        self.type_search_combobox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SearchWindow)

    def retranslateUi(self, SearchWindow):
        _translate = QtCore.QCoreApplication.translate
        SearchWindow.setWindowTitle(_translate("SearchWindow", "Pesquisar"))
        self.type_label.setText(_translate("SearchWindow", "{area}"))
        self.btn_close.setText(_translate("SearchWindow", " Cancelar"))
        self.search_label.setText(_translate("SearchWindow", "Pesquisar"))
        self.btn_ok.setText(_translate("SearchWindow", " OK"))
        self.type_search_combobox.setCurrentText(_translate("SearchWindow", "Código"))
        self.type_search_combobox.setItemText(0, _translate("SearchWindow", "Código"))
        self.type_search_combobox.setItemText(1, _translate("SearchWindow", "Descrição"))
        self.type_search_label.setText(_translate("SearchWindow", "Critério"))
from src.qt.ui import resource_rc