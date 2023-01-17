import sys

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QSpacerItem
from assets.scripts.path_module import path_to_asset
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic


class UserEntry(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        uic.loadUi(path_to_asset('uis', 'user_state.ui'), self)

    def set_username(self, name):
        self.label.setText(name)


class PermissionWindow(QWidget):
    permission_changed = pyqtSignal(list, str)

    def __init__(self, maps, users):
        super().__init__()
        uic.loadUi(path_to_asset('uis', 'permissions_form.ui'), self)
        self.submitButton.clicked.connect(self.change_info)
        self.comboBox.addItems(maps)
        self.names = list()
        self.checkboxes = list()

        layout = QVBoxLayout()
        for username, state in users:
            win = UserEntry(self.scrollArea)
            win.set_username(username)
            win.checkBox.setTristate(False)
            win.checkBox.setCheckState(state)
            layout.addWidget(win)
            self.names.append(username)
            self.checkboxes.append(win.checkBox)

        layout.addSpacerItem(QSpacerItem(0, 999))
        self.scrollArea.setLayout(layout)

    def change_info(self):
        new_info = list()
        for name, checkbox in zip(self.names, self.checkboxes):
            new_info.append((name, bool(checkbox.checkState())))
        self.permission_changed.emit(new_info, self.comboBox.currentText())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = PermissionWindow('test', [['QQQQ', True], ['DDD', False], ['Damn daniel', True]])
    window.permission_changed.connect(lambda x: print(x))
    window.show()

    sys.exit(app.exec_())
