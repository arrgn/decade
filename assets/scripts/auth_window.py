from PyQt5 import Qt, uic
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QLabel, QComboBox
from assets.scripts.path_module import path_to_file
from assets.scripts.config import user


class AuthWindow(QDialog):
    def __init__(self, is_login: bool):
        super().__init__()
        self.is_login = is_login
        self.auth_btn = QPushButton()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.users = QComboBox
        self.error = QLabel()  # Label to show status or errors

        self.init_ui()

    def init_ui(self):
        if not self.is_login:
            uic.loadUi(path_to_file("assets", "uis", "sign_up.ui"), self)
        else:
            uic.loadUi(path_to_file("assets", "uis", "sign_in.ui"), self)

        # Configure window to work with reg or login
        if self.is_login:
            self.auth_btn.setText("Sign In")
            users = user.get_users()
            for el in users:
                self.users.addItem(el[0])
            self.auth_btn.clicked.connect(self.login)
        else:
            self.auth_btn.clicked.connect(self.register)

        self.show()

    def register(self):
        name = self.username.text()
        password = self.password.text()
        res = user.add_user(name, password)
        if not res:
            self.error.setText(f"User with name {name} exists!")
            return
        self.error.setText(f"User {name} created. Successfully sign in via user {name}.")

    def login(self):
        name = self.users.currentText()
        password = self.password.text()
        res = user.set_user(name, password)
        if not res:
            self.error.setText(f"Can't sig in via {name}!")
            return
        self.error.setText(f"Successfully sign in via user {name}.")
