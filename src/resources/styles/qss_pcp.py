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
                margin: 10px 0 20px 0;
                font-size: 18px;
                font-weight: bold;
                font-style: "Segoe UI";
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
                background-color: #0d6efd;
                color: #FFFFFF;
                padding: 7px 10px;
                border: 2px solid #0d6efd;
                border-radius: 10px;
                font-size: 18px;
                height: 32px;
                font-weight: 400;
                margin: 0px 5px 10px 5px;
            }
            
            QPushButton#btn_home {
                background-color: #dc3545; /* Bootstrap danger */
                border-color: #dc3545;
            }

            QPushButton:hover, QPushButton:hover#btn_home { 
                background-color: #0b5ed7;
                border-color: #0a58ca;
            }

            QPushButton#btn_home:hover {
                background-color: #bb2d3b;
                border-color: #b02a37;
            }

            QPushButton:pressed, QPushButton:pressed#btn_home { 
                background-color: #0a58ca;
                border-color: #0a53be;
            }

            QTableWidget {
                border: 1px solid #000000;
                padding-left: 10px;
                margin: 0;
                alternate-background-color: #f8f9fa;
                gridline-color: transparent; /* Remove vertical grid lines */
            }
            
            QTableWidget#result_table {
                background-color: #EEEEEE;
            }
            
            QTableWidget#table_area {
                background-color: #373A40;
            }

            QTableWidget QHeaderView::section {
                background-color: #262626;
                color: #EEEEEE;
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
            }"""
