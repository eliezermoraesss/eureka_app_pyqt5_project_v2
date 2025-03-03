def vendas_qss():
    return """* {
                background-color: #363636;
                font-style: 'Segoe UI';
            }
    
            QLabel {
                color: #DFE0E2;
                font-size: 13px;
                font-weight: regular;
                padding-left: 10px; 
                font-style: "Segoe UI";
            }
            
            QLabel#label-title {
                margin: 5px;
                font-size: 22px;
                font-weight: bold;
            }
            
            QLabel#logo-enaplic {
                margin: 5px;
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
            
            QComboBox QAbstractItemView {
                background-color: #EEEEEE;
                color: #000000; /* Cor do texto para garantir legibilidade */
                selection-background-color: #3f37c9; /* Cor de seleção quando passa o mouse */
                selection-color: #FFFFFF; /* Cor do texto quando selecionado */
                border: 1px solid #393E46;
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
                border: 1px solid #000000;
                padding: 5px 10px;
                border-radius: 12px;
                font-size: 16px;
            }
            
            QLineEdit#cliente {
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 16px;
                margin-bottom:  10px;
            }
    
            QPushButton {
                background-color: #3f37c9;
                border: 1px solid #3a0ca3;
                color: #eeeeee;
                padding: 5px 10px;
                border-radius: 8px;
                font-style: "Segoe UI";
                font-size: 11px;
                height: 24px;
                font-weight: bold;
                margin: 5px;
            }
            
            QPushButton#btn_home {
                background-color: #c1121f;
            }
    
            QPushButton:hover, QPushButton:hover#btn_home {
                background-color: #EFF2F1;
                color: #3A0CA3
            }
    
            QPushButton:pressed, QPushButton:pressed#btn_home {
                background-color: #6703c5;
                color: #fff;
            }
            
            QTableWidget {
                border: 1px solid #000000;
            }
            
            QTableWidget#result_table {
                background-color: #EEEEEE;
            }
            
            QTableWidget#table_area {
                background-color: #363636;
            }
            
            QTableWidget QHeaderView::section {
                background-color: #393E46;
                color: #EEEEEE;
                font-weight: bold;
                height: 25px;
            }
    
            QTableWidget QHeaderView::section:horizontal {
                border-top: 1px solid #393E46;
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
            }
            
            QFrame#line {
                color: white;
                background-color: white;
                border: 1px solid white;
                margin-bottom: 3px;
            }"""
