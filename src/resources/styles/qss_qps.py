def qps_qss():
    return """* {
                background-color: #222831;
            }

            QLabel {
                color: #DFE0E2;
                font-size: 12px;
                font-weight: bold;
                padding-left: 3px;
            }
            
            QLabel#label-line-number {
                font-size: 16px;
                font-weight: normal;
            }
            
            QLabel#label-title {
                margin: 10px;
                font-size: 30px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #EEEEEE;
                border: 1px solid #262626;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }

            QPushButton {
                background-color: #00ADB5;
                color: #EEEEEE;
                padding: 5px 10px;
                border: 2px;
                border-radius: 8px;
                font-size: 11px;
                height: 20px;
                font-weight: bold;
                margin: 10px 5px;
            }
            
            QPushButton#btn_home {
                background-color: #c1121f;
            }
            
            QPushButton#btn_atualizar_qp {
                background-color: #3F72AF;
            }

            QPushButton:hover, QPushButton:hover#btn_atualizar_qp, QPushButton:hover#btn_home { 
                background-color: #E84545; color: #fff 
            }
    
            QPushButton:pressed, QPushButton:pressed#btn_atualizar_qp, QPushButton:pressed#btn_home {
                background-color: #6703c5; color: #fff; 
            }

            QTableWidget {
                border: 1px solid #000000;
                background-color: #393E46;
                padding-left: 10px;
                margin: 5px 0;
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
                background-color: #393E46;
                color: #fff;
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
