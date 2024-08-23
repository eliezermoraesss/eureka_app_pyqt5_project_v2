from ..views.main_window import MainWindow
import subprocess


class MainController:
    def __init__(self):
        self.main_window = MainWindow()
        self.setup_connections()

    def setup_connections(self):
        def execute_engenharia_model():
            script_path = "src/models/engenharia_model.pyw"
            subprocess.run(["python", script_path])

        def execute_comercial_model():
            script_path = "src/models/comercial_model.pyw"
            subprocess.run(["python", script_path])

        def execute_pcp_model():
            script_path = "src/models/pcp_model.pyw"
            subprocess.run(["python", script_path])

        self.main_window.engenharia_button.clicked.connect(execute_engenharia_model)
        self.main_window.comercial_button.clicked.connect(execute_comercial_model)
        self.main_window.pcp_button.clicked.connect(execute_pcp_model)

    def show_main_window(self):
        self.main_window.show()
