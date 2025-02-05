def compras_qss():
    return """* {
                background-color: #111827;
            }
    
            QLabel, QCheckBox {
                color: #DFE0E2;
                font-size: 13px;
                font-weight: regular;
                padding-left: 10px; 
                font-style: "Segoe UI";
            }
            
            QCheckBox#checkbox-sc {
                margin-left: 10px;
                font-size: 13px;
                font-weight: normal;
            }
            
            QLabel#label-line-number {
                font-size: 16px;
                font-weight: normal;
            }
    
            QDateEdit, QComboBox {
                background-color: #EEEEEE;
                border: 1px solid #393E46;
                margin-bottom: 10px;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }
    
            QDateEdit::drop-down, QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
    
            QDateEdit::down-arrow, QComboBox::down-arrow {
                image: url(../resources/images/arrow.png);
                width: 10px;
                height: 10px;
            }
    
            QLineEdit {
                background-color: #EEEEEE;
                border: 1px solid #393E46;
                padding: 5px 10px;
                border-radius: 12px;
                font-size: 16px;
            }
            
            QLineEdit#forn-raz, QLineEdit#forn-fantasia, QLineEdit#armazem {
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 16px;
                margin-bottom:  10px;
            }
    
            QPushButton {
                background-color: #5603ad;
                color: #FFFFFF;
                padding: 5px 8px;
                border: 1px solid #5603ad;
                border-radius: 8px;
                font-style: "Segoe UI";
                font-size: 12px;
                height: 22px;
                font-weight: bold;
                margin: 5px;
            }
            
            QPushButton#btn_home {
                background-color: #c1121f;
            }
    
            QPushButton:hover, QPushButton:hover#btn_home {
                background-color: #2A6F97;
                font-weight: bold;
            }
    
            QPushButton:pressed, QPushButton:pressed#btn_home {
                background-color: #6703c5;
                color: #fff;
            }
            
            QTableWidget {
                border: 1px solid #111827;
            }
            
            QTableWidget#result_table {
                background-color: #EEEEEE;
            }
            
            QTableWidget#table_area {
                background-color: #111827;
            }
            
            QTableWidget QHeaderView::section {
                background-color: #302c2c;
                color: #EEEEEE;
                font-weight: bold;
                height: 25px;
            }
    
            QTableWidget QHeaderView::section:horizontal {
                border-top: 1px solid #000000;
                font-size: 11px;
                font-weight: bold;
                padding: 5px;
                height: 25px;
            }
    
            QTableWidget::item {
                font-weight: bold;
                padding-left: 10px;
            }
            
            QTableWidget::item:selected {
                color: #EEEEEE;
                font-weight: bold;
            }"""
