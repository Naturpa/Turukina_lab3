import sys
import random
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor


class FlagGenerator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('flag_generator.ui', self)

        # Инициализация переменных
        self.current_flag = None
        self.stripes_count = 0
        self.colors = []

        # Подключение сигналов
        self.generateButton.clicked.connect(self.generate_flag)
        self.saveButton.clicked.connect(self.save_flag)

        # Обновление интерфейса
        self.update_controls()

    def generate_flag(self):
        """Генерация флага"""
        # Диалог выбора количества полос
        stripes, ok = QInputDialog.getInt(
            self,
            "Количество полос",
            "Введите количество цветных полос (3-12):",
            value=5,
            min=3,
            max=12,
            step=1
        )

        if ok:
            self.stripes_count = stripes
            self.create_striped_flag()

    def create_striped_flag(self):
        """Создание полосатого флага"""
        try:
            # Генерация случайных цветов
            self.colors = self.generate_random_colors(self.stripes_count)

            # Размеры флага
            flag_width = 600
            flag_height = 400
            stripe_height = flag_height // self.stripes_count

            # Создание изображения флага
            flag_image = QPixmap(flag_width, flag_height)
            painter = QPainter(flag_image)

            # Рисование полос
            for i in range(self.stripes_count):
                color = self.colors[i]
                y_position = i * stripe_height

                # Если это последняя полоса, растягиваем до конца
                if i == self.stripes_count - 1:
                    stripe_height_final = flag_height - y_position
                else:
                    stripe_height_final = stripe_height

                painter.fillRect(0, y_position, flag_width, stripe_height_final, color)

            painter.end()

            # Сохранение и отображение флага
            self.current_flag = flag_image
            self.display_flag(flag_image)

            # Обновление информации
            self.infoLabel.setText(f"Количество полос: {self.stripes_count}")
            color_names = [f"RGB({color.red()},{color.green()},{color.blue()})"
                           for color in self.colors]
            self.statusbar.showMessage(f"Сгенерирован флаг с {self.stripes_count} полосами: {', '.join(color_names)}")

        except Exception as e:
            self.show_error(f"Ошибка при создании флага: {str(e)}")

    def generate_random_colors(self, count):
        """Генерация случайных цветов"""
        colors = []
        for _ in range(count):
            # Генерация случайного RGB цвета
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            colors.append(QColor(red, green, blue))
        return colors

    def display_flag(self, flag_pixmap):
        """Отображение флага в интерфейсе"""
        if flag_pixmap:
            # Масштабирование для отображения с сохранением пропорций
            label_size = self.flagLabel.size()
            scaled_pixmap = flag_pixmap.scaled(
                label_size.width() - 20,
                label_size.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.flagLabel.setPixmap(scaled_pixmap)

    def save_flag(self):
        """Сохранение флага в файл"""
        if self.current_flag is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала сгенерируйте флаг")
            return

        try:
            # Диалог сохранения файла
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить флаг",
                f"flag_{self.stripes_count}_stripes.png",
                "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
            )

            if file_path:
                # Сохранение изображения
                success = self.current_flag.save(file_path)
                if success:
                    self.statusbar.showMessage(f"Флаг сохранен: {file_path}")
                    QMessageBox.information(self, "Успех", f"Флаг успешно сохранен в файл:\n{file_path}")
                else:
                    self.show_error("Не удалось сохранить флаг")

        except Exception as e:
            self.show_error(f"Ошибка при сохранении флага: {str(e)}")

    def update_controls(self):
        """Обновление состояния элементов управления"""
        has_flag = self.current_flag is not None
        self.saveButton.setEnabled(has_flag)

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)
        self.statusbar.showMessage(f"Ошибка: {message}")

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        if self.current_flag:
            self.display_flag(self.current_flag)


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = FlagGenerator()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
