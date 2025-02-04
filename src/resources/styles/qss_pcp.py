def pcp_qss():
    return """* {
                background-color: #373A40;
            }

            QLabel {
                color: #DFE0E2;
                font-size: 12px;
                font-weight: bold;
                padding-left: 3px;
            }
            
            QLabel#label-line-number, QLabel#label-indicators {
                font-size: 14px;
                font-weight: bold;
            }
            
            QLabel#label-title {
                margin: 10px;
                font-size: 30px;
                font-weight: bold;
            }
            
            QDateEdit {
                background-color: #DFE0E2;
                border: 1px solid #262626;
                margin-bottom: 20px;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }
            
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            
            QDateEdit::down-arrow {
                image: url(../resources/images/arrow.png);
                width: 10px;
                height: 10px;
            }

            QLineEdit {
                background-color: #EEEEEE;
                border: 1px solid #262626;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }
            
            QComboBox {
                background-color: #EEEEEE;
                border: 1px solid #393E46;
                margin-bottom: 10px;
                padding: 5px 10px;
                border-radius: 10px;
                height: 20px;
                font-size: 16px;
            }                 
            
            QComboBox QAbstractItemView {
                background-color: #EEEEEE;
                color: #000000; /* Cor do texto para garantir legibilidade */
                selection-background-color: #3f37c9; /* Cor de seleção quando passa o mouse */
                selection-color: #FFFFFF; /* Cor do texto quando selecionado */
                border: 1px solid #393E46;
            }

            QPushButton {
                background-color: #EB5B00;
                color: #EEEEEE;
                padding: 7px 10px;
                border: 2px;
                border-radius: 8px;
                font-size: 12px;
                height: 20px;
                font-weight: bold;
                margin: 0px 5px 10px 5px;
            }
            
            QPushButton#btn_home {
                background-color: #c1121f;
            }

            QPushButton:hover, QPushButton:hover#btn_home { background-color: #E84545; color: #fff }
    
            QPushButton:pressed, QPushButton:pressed#btn_home { background-color: #6703c5; color: #fff; }

            QTableWidget {
                border: 1px solid #000000;
                background-color: #EEEEEE;
                padding-left: 10px;
                margin: 0;
            }

            QTableWidget QHeaderView::section {
                background-color: #262626;
                color: #A7A6A6;
                padding: 5px;
                height: 18px;
            }

            QTableWidget QHeaderView::section:horizontal {
                border-top: 1px solid #333;
            }

            QTableWidget::item {
                color: #000000;
                font-weight: bold;
                padding-right: 8px;
                padding-left: 8px;
            }

            QTableWidget::item:selected {
                background-color: #000000;
                color: #EEEEEE;
                font-weight: bold;
            }
            
            QFrame#line {
                color: white;
                background-color: white;
                border: 1px solid white;
                margin-bottom: 3px;
            }"""
