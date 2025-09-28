import sys
import math
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QColorDialog, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush


class SmileyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.smiley_color = QColor(255, 255, 0)  # Желтый по умолчанию
        self.scale_factor = 1.0

    def set_smiley_color(self, color):
        self.smiley_color = color
        self.update()  # Перерисовываем виджет

    def set_scale_factor(self, scale):
        self.scale_factor = scale / 100.0
        self.update()  # Перерисовываем виджет

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Сглаживание

        # Размеры виджета
        width = self.width()
        height = self.height()

        # Центр смайлика
        center_x = width // 2
        center_y = height // 2

        # Базовый размер смайлика (при масштабе 100%)
        base_size = min(width, height) * 0.8

        # Применяем масштаб
        size = base_size * self.scale_factor

        # Рисуем смайлик
        self.draw_smiley(painter, center_x, center_y, size)

    def draw_smiley(self, painter, center_x, center_y, size):
        """Рисование смайлика"""
        # Основной круг (лицо)
        face_radius = size / 2
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(self.smiley_color))
        painter.drawEllipse(int(center_x - face_radius), int(center_y - face_radius),
                            int(size), int(size))

        # Глаза
        eye_radius = face_radius * 0.15
        eye_offset_x = face_radius * 0.3
        eye_offset_y = face_radius * 0.25

        # Левый глаз
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(int(center_x - eye_offset_x - eye_radius),
                            int(center_y - eye_offset_y - eye_radius),
                            int(eye_radius * 2), int(eye_radius * 2))

        # Правый глаз
        painter.drawEllipse(int(center_x + eye_offset_x - eye_radius),
                            int(center_y - eye_offset_y - eye_radius),
                            int(eye_radius * 2), int(eye_radius * 2))

        # Улыбка
        smile_radius = face_radius * 0.5
        smile_start_angle = 220 * 16  # В градусах * 16 (Qt использует 1/16 градуса)
        smile_span_angle = 100 * 16  # Длина дуги

        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(int(center_x - smile_radius), int(center_y - smile_radius * 0.7),
                        int(smile_radius * 2), int(smile_radius * 2),
                        smile_start_angle, smile_span_angle)


class SmileyPainter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('smiley_painter.ui', self)

        # Инициализация переменных
        self.smiley_color = QColor(255, 255, 0)  # Желтый по умолчанию
        self.scale_factor = 100  # 100%

        # Создаем и настраиваем виджет для рисования смайлика
        self.smiley_widget = SmileyWidget()

        # Заменяем стандартный виджет на наш кастомный
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.smiley_widget)
        self.smileyWidget.setLayout(layout)

        # Установка начального цвета
        self.smiley_widget.set_smiley_color(self.smiley_color)
        self.update_color_display()

        # Подключение сигналов
        self.colorButton.clicked.connect(self.choose_color)
        self.scaleSlider.valueChanged.connect(self.scale_changed)

        # Обновление интерфейса
        self.update_scale_display()

        self.statusbar.showMessage("Готов к рисованию смайлика!")

    def choose_color(self):
        """Выбор цвета смайлика"""
        color = QColorDialog.getColor(self.smiley_color, self, "Выберите цвет смайлика")

        if color.isValid():
            self.smiley_color = color
            self.smiley_widget.set_smiley_color(color)
            self.update_color_display()
            self.statusbar.showMessage(f"Цвет изменен на RGB({color.red()}, {color.green()}, {color.blue()})")

    def scale_changed(self, value):
        """Обработчик изменения масштаба"""
        self.scale_factor = value
        self.smiley_widget.set_scale_factor(value)
        self.update_scale_display()
        self.statusbar.showMessage(f"Масштаб установлен: {value}%")

    def update_color_display(self):
        """Обновление отображения текущего цвета"""
        # Устанавливаем цвет фона метки в выбранный цвет
        self.colorLabel.setStyleSheet(f"background-color: {self.smiley_color.name()};")
        self.colorLabel.setText(
            f"RGB({self.smiley_color.red()}, {self.smiley_color.green()}, {self.smiley_color.blue()})")

    def update_scale_display(self):
        """Обновление отображения текущего масштаба"""
        self.scaleLabel.setText(f"{self.scale_factor}%")


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = SmileyPainter()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()