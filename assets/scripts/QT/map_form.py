import sys

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QFileDialog, QTableWidget, QInputDialog, QTableWidgetItem,
                             QWidget)
from datetime import date


class FormWindow(QWidget):
    map_added = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        uic.loadUi('assets/uis/map_maker.ui', self)
        self.waveTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.map_file = None
        self.waves = list()
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

        if self.waveTable.rowCount() == 0:
            return self.errorLabel.setText('Информации о волнах нет.')

        info = {
            map_name: {
                "TILE_WIDTH": tile_size,
                "TILE_HEIGHT": tile_size,
                "LEVEL_SIZE": (tile_size * level_size_x, tile_size * level_size_y),
                "SUN_POSITION": (sun_pos_x, sun_pos_y),
                "DESCRIPTION": description_input,
                "DATE": date.today().strftime('%d.%m.%Y'),
                "FILE_NAME": self.map_file,
                "ACCESS": 'PUBLIC' if is_public else 'PRIVATE',
                "TIME_BREAKS": timer_break,
                "WAVES": {i: value for i, value in enumerate(self.waves, start=1)}
            }
        }

        self.map_added.emit(info)
        self.close()

    def open_file_dialog(self):
        filepath = QFileDialog.getOpenFileName(self, 'Choose map', '', 'Map (*.tmx)')[0]
        if filepath:
            self.map_file = filepath
            self.chooseMapButton.setText('Карта загружена.')
            self.chooseMapButton.setEnabled(False)

    def add_wave(self):
        amount, ok_pressed = QInputDialog.getInt(
            self, "Ввод информации", "Введите количество врагов",
            15, 1, 99, 1)

        self.waves.append(amount)
        if ok_pressed:
            rowCount = self.waveTable.rowCount() + 1
            self.waveTable.setRowCount(rowCount)

            data2 = QTableWidgetItem()
            data2.setData(Qt.ItemDataRole.DisplayRole, amount)
            self.waveTable.setItem(rowCount - 1, 0, data2)

    def remove_wave(self):
        rowCount = self.waveTable.rowCount()
        if rowCount > 0:
            self.waveTable.setRowCount(rowCount - 1)
            self.waves.pop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormWindow()
    window.show()
    sys.exit(app.exec_())
