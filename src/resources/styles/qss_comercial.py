def comercial_qss():
    return """* {
                    background-color: #363636;
                    font-family: "Segoe UI";
                }
    
                QLabel {
                    color: #EEEEEE;
                    font-size: 14px;
                    font-weight: regular;
                    padding-left: 5px;
                }
                
                QLabel#product-name {
                    font-size: 20px;
                    font-weight: bold;
                }
                
                QLabel#label-costs {
                    font-size: 16px;
                    font-weight: regular;
                }
    
                QLineEdit {
                    background-color: #EEEEEE;
                    border: 1px solid #C9C9C9;
                    padding: 10px;
                    border-radius: 14px;
                    height: 20px;
                    font-size: 14px;
                }
    
                QPushButton {
                    background-color: #3f7c24;
                    color: #fff;
                    padding: 10px;
                    border: 2px;
                    border-radius: 18px;
                    font-size: 14px;
                    height: 24px;
                    font-weight: regular;
                    margin-top: 20px;
                    margin-left: 10px;
                }
                
                QPushButton#btn_home {
                    background-color: #c1121f;
                }
    
                QPushButton:hover, QPushButton:hover#btn_home {
                    background-color: #DC5F00;
                    color: #EEEEEE;
                }
    
                QPushButton:pressed, QPushButton:pressed#btn_home {
                    background-color: #6703c5;
                    color: #fff;
                }
    
                QTableWidget {
                    font-family: "Segoe UI";
                    border: 1px solid #000000;
                    background-color: #262626;
                    padding-left: 10px;
                    margin: 15px 0;
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
                    background-color: #363636;
                    color: #EEEEEE;
                    font-weight: bold;
                    padding-right: 8px;
                    padding-left: 8px;
                }
    
                QTableWidget::item:selected {
                    background-color: #000000;
                    color: #EEEEEE;
                    font-weight: bold;
                }"""
