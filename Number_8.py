import sys
import os
import math
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor


class LSystem:
    def __init__(self):
        self.name = ""
        self.angle = 0
        self.axiom = ""
        self.rules = {}
        self.current_string = ""
        self.steps = [""]  # История эволюции
        self.current_step = 0

    def load_from_file(self, filename):
        """Загрузка L-системы из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]

            if len(lines) < 3:
                raise ValueError("Файл должен содержать минимум 3 строки")

            self.name = lines[0]
            self.angle = 360 / int(lines[1])  # Преобразуем в угол поворота
            self.axiom = lines[2]
            self.rules = {}

            # Чтение правил
            for line in lines[3:]:
                if ' ' in line:
                    key, value = line.split(' ', 1)
                    self.rules[key.strip()] = value.strip()

            # Инициализация
            self.current_string = self.axiom
            self.steps = [self.axiom]
            self.current_step = 0

            return True

        except Exception as e:
            raise ValueError(f"Ошибка чтения файла: {str(e)}")

    def evolve(self, steps=1):
        """Эволюция системы на указанное количество шагов"""
        for _ in range(steps):
            new_string = ""
            for char in self.current_string:
                if char in self.rules:
                    new_string += self.rules[char]
                else:
                    new_string += char
            self.current_string = new_string
            self.steps.append(new_string)

    def set_step(self, step):
        """Установка текущего шага эволюции"""
        if 0 <= step < len(self.steps):
            self.current_step = step
            self.current_string = self.steps[step]

    def get_current_string(self):
        """Получение текущей строки"""
        return self.current_string

    def get_max_steps(self):
        """Получение максимального количества шагов"""
        return len(self.steps) - 1


class LSystemWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lsystem = None
        self.pen_color = QColor(0, 100, 200)
        self.bg_color = QColor(240, 240, 240)

    def set_lsystem(self, lsystem):
        """Установка L-системы для отображения"""
        self.lsystem = lsystem
        self.update()

    def paintEvent(self, event):
        """Отрисовка L-системы"""
        if not self.lsystem or not self.lsystem.current_string:
            # Отрисовка пустого состояния
            painter = QPainter(self)
            painter.fillRect(self.rect(), self.bg_color)
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(self.rect(), Qt.AlignCenter, "Загрузите L-систему для отображения")
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Очистка фона
        painter.fillRect(self.rect(), self.bg_color)

        # Настройка пера
        pen = QPen(self.pen_color)
        pen.setWidth(2)
        painter.setPen(pen)

        # Параметры отрисовки
        width = self.width()
        height = self.height()
        start_x = width // 2
        start_y = height - 50  # Начинаем снизу
        line_length = min(width, height) / (2 ** (self.lsystem.current_step * 0.3))

        # Стек для сохранения состояний (для символов '[' и ']')
        stack = []
        x, y = start_x, start_y
        angle = -90  # Начальный угол (вверх)

        # Отрисовка согласно текущей строке
        for char in self.lsystem.current_string:
            if char == 'F' or char == 'G':
                # Рисуем линию вперед
                new_x = x + line_length * math.cos(math.radians(angle))
                new_y = y + line_length * math.sin(math.radians(angle))
                painter.drawLine(int(x), int(y), int(new_x), int(new_y))
                x, y = new_x, new_y
            elif char == 'f':
                # Перемещаемся вперед без рисования
                new_x = x + line_length * math.cos(math.radians(angle))
                new_y = y + line_length * math.sin(math.radians(angle))
                x, y = new_x, new_y
            elif char == '+':
                # Поворот влево
                angle += self.lsystem.angle
            elif char == '-':
                # Поворот вправо
                angle -= self.lsystem.angle
            elif char == '[':
                # Сохраняем текущее состояние
                stack.append((x, y, angle))
            elif char == ']':
                # Восстанавливаем предыдущее состояние
                if stack:
                    x, y, angle = stack.pop()

        # Отображение информации о текущем шаге
        painter.setPen(QColor(0, 0, 0))
        info_text = f"Шаг: {self.lsystem.current_step}, Длина строки: {len(self.lsystem.current_string)}"
        painter.drawText(10, 20, info_text)


class LSystemViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('lsystem_viewer.ui', self)

        # Инициализация L-системы
        self.lsystem = LSystem()

        # Создание и настройка виджета отрисовки
        self.lsystem_widget = LSystemWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.lsystem_widget)
        self.drawingArea.setLayout(layout)

        # Подключение сигналов
        self.loadButton.clicked.connect(self.load_system)
        self.stepSlider.valueChanged.connect(self.slider_changed)
        self.prevButton.clicked.connect(self.previous_step)
        self.nextButton.clicked.connect(self.next_step)
        self.resetButton.clicked.connect(self.reset_system)

        # Обновление интерфейса
        self.update_controls()

        # Автоматическая загрузка файла при старте
        QTimer.singleShot(100, self.auto_load_system)

        self.statusbar.showMessage("Готов к загрузке L-системы")

    def auto_load_system(self):
        """Автоматическая загрузка L-системы при старте"""
        self.load_system()

    def load_system(self):
        """Загрузка L-системы из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл L-системы",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                # Создаем новую L-систему и загружаем из файла
                self.lsystem = LSystem()
                self.lsystem.load_from_file(file_path)

                # Автоматически генерируем первый шаг эволюции
                self.lsystem.evolve(1)

                # Обновляем интерфейс
                self.lsystem_widget.set_lsystem(self.lsystem)
                self.update_display()
                self.update_controls()

                # Устанавливаем слайдер на первый шаг
                self.stepSlider.setMaximum(self.lsystem.get_max_steps())
                self.stepSlider.setValue(1)  # Первый шаг после аксиомы

                file_name = os.path.basename(file_path)
                self.statusbar.showMessage(f"Загружена система: {self.lsystem.name}")

            except Exception as e:
                self.show_error(f"Ошибка загрузки системы: {str(e)}")

    def slider_changed(self, value):
        """Обработчик изменения слайдера"""
        self.lsystem.set_step(value)
        self.lsystem_widget.set_lsystem(self.lsystem)
        self.update_display()
        self.statusbar.showMessage(f"Установлен шаг: {value}")

    def previous_step(self):
        """Переход к предыдущему шагу"""
        current = self.stepSlider.value()
        if current > 0:
            self.stepSlider.setValue(current - 1)

    def next_step(self):
        """Переход к следующему шагу"""
        current = self.stepSlider.value()
        if current < self.stepSlider.maximum():
            # Если это последний существующий шаг, генерируем следующий
            if current == self.lsystem.get_max_steps():
                self.lsystem.evolve(1)
                self.stepSlider.setMaximum(self.lsystem.get_max_steps())

            self.stepSlider.setValue(current + 1)

    def reset_system(self):
        """Сброс системы к начальному состоянию"""
        if self.lsystem and self.lsystem.get_max_steps() > 0:
            self.stepSlider.setValue(0)
            self.statusbar.showMessage("Система сброшена к начальному состоянию")

    def update_display(self):
        """Обновление отображения информации о системе"""
        if self.lsystem and self.lsystem.name:
            self.systemNameLabel.setText(self.lsystem.name)
            self.stepLabel.setText(str(self.lsystem.current_step))
            self.maxStepLabel.setText(str(self.lsystem.get_max_steps()))
            self.axiomLabel.setText(f"Аксиома: {self.lsystem.axiom}")
            self.angleLabel.setText(f"Угол: {self.lsystem.angle:.1f}°")

            rules_text = "Правила: " + ", ".join([f"{k}→{v}" for k, v in self.lsystem.rules.items()])
            if len(rules_text) > 50:
                rules_text = rules_text[:47] + "..."
            self.rulesLabel.setText(rules_text)
        else:
            self.systemNameLabel.setText("Система не загружена")
            self.stepLabel.setText("0")
            self.maxStepLabel.setText("0")
            self.axiomLabel.setText("Аксиома: не задана")
            self.angleLabel.setText("Угол: не задан")
            self.rulesLabel.setText("Правила: не заданы")

    def update_controls(self):
        """Обновление состояния элементов управления"""
        has_system = self.lsystem and self.lsystem.get_max_steps() > 0
        self.stepSlider.setEnabled(has_system)
        self.prevButton.setEnabled(has_system)
        self.nextButton.setEnabled(has_system)
        self.resetButton.setEnabled(has_system)

        if has_system:
            current_step = self.stepSlider.value()
            self.prevButton.setEnabled(current_step > 0)
            self.nextButton.setEnabled(current_step < self.stepSlider.maximum())

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)
        self.statusbar.showMessage(f"Ошибка: {message}")


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = LSystemViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
