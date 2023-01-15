import sys

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QFileDialog, QTableWidgetItem, QTableWidget, QInputDialog,
                             QWidget)


class FormWindow(QWidget):
    map_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('assets/uis/map_maker.ui', self)
        self.waveTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.map_file = None
        self.waves = dict()
        self.submitButton.clicked.connect(self.on_submit)
        self.addWave.clicked.connect(self.add_wave)
        self.removeWave.clicked.connect(self.remove_wave)
        self.chooseMapButton.clicked.connect(self.open_file_dialog)

    def on_submit(self):
        map_name = self.mapNameInput.text()
        tile_size = self.tileSize.value()
        level_size_x = self.levelSizeX.value()
        level_size_y = self.levelSizeY.value()
        sun_pos_x = self.sunPosX.value()
        sun_pos_y = self.sunPosY.value()
        timer_break = self.timerBreakInput.value()
        description_input = self.descriptionInput.toPlainText()
        is_public = bool(self.publicCheckbox.checkState())

        if not self.map_file:
            return self.errorLabel.setText('Ошибка: Файл не выбран!')

        # print(map_name, tile_size, level_size_x, level_size_y,
        #      sun_pos_x, sun_pos_y, timer_break, description_input, is_public)

    def open_file_dialog(self):
        filepath = QFileDialog.getOpenFileName(self, 'Choose map', '', 'Map (*.tmx)')[0]
        if filepath:
            print(filepath)
            self.map_file = filepath
            self.chooseMapButton.setText('Карта загружена.')
            self.chooseMapButton.setEnabled(False)

    def add_wave(self):
        amount, ok_pressed = QInputDialog.getInt(
            self, "Ввод информации", "Введите количество врагов",
            15, 1, 99, 1)

        if ok_pressed:
            print(str(amount))
            rowCount = self.waveTable.rowCount() + 1
            self.waveTable.setRowCount(rowCount)
            self.waveTable.setItem(0, rowCount, QTableWidgetItem(str(rowCount)))
            self.waveTable.setItem(1, rowCount, QTableWidgetItem(str(amount)))

    def remove_wave(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormWindow()
    window.show()
    sys.exit(app.exec_())
