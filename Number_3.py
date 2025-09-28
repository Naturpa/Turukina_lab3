import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QTransform, QColor


class ImageEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('image_editor.ui', self)

        # Инициализация переменных
        self.original_pixmap = None
        self.current_pixmap = None
        self.rotation_angle = 0

        # Подключение сигналов
        self.loadButton.clicked.connect(self.load_image)
        self.rotateLeftButton.clicked.connect(self.rotate_left)
        self.rotateRightButton.clicked.connect(self.rotate_right)
        self.resetRotationButton.clicked.connect(self.reset_rotation)

        # Подключение радиокнопок
        self.originalRadio.toggled.connect(self.update_image_display)
        self.redChannelRadio.toggled.connect(self.update_image_display)
        self.greenChannelRadio.toggled.connect(self.update_image_display)
        self.blueChannelRadio.toggled.connect(self.update_image_display)
        self.grayscaleRadio.toggled.connect(self.update_image_display)

        # Обновление интерфейса
        self.update_controls()

        # Автоматическое открытие диалога выбора изображения при старте
        QTimer.singleShot(100, self.load_image)

    def load_image(self):
        """Загрузка изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )

        if file_path:
            try:
                # Загрузка изображения с помощью QPixmap
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    self.show_error("Не удалось загрузить изображение")
                    return

                # Проверка, что изображение квадратное
                if pixmap.width() != pixmap.height():
                    # Если не квадратное, делаем его квадратным
                    size = min(pixmap.width(), pixmap.height())
                    pixmap = pixmap.copy(0, 0, size, size)
                    QMessageBox.information(self, "Информация",
                                            "Изображение было обрезано до квадратной формы")

                # Сохранение оригинального изображения
                self.original_pixmap = pixmap
                self.current_pixmap = pixmap
                self.rotation_angle = 0

                # Обновление интерфейса
                file_name = os.path.basename(file_path)
                self.fileNameLabel.setText(f"Загружено: {file_name}")
                self.update_image_display()
                self.update_controls()

                self.statusbar.showMessage(f"Изображение загружено: {file_name}")

            except Exception as e:
                self.show_error(f"Ошибка при загрузке изображения: {str(e)}")

    def apply_color_channel(self, pixmap):
        """Применение выбранного цветового канала"""
        if self.originalRadio.isChecked() or self.original_pixmap is None:
            return pixmap

        # Создаем QImage для манипуляций с пикселями
        image = pixmap.toImage()

        # Обрабатываем каждый пиксель
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                r, g, b = color.red(), color.green(), color.blue()

                if self.redChannelRadio.isChecked():
                    # Оставляем только красный канал
                    new_color = QColor(r, 0, 0)
                elif self.greenChannelRadio.isChecked():
                    # Оставляем только зеленый канал
                    new_color = QColor(0, g, 0)
                elif self.blueChannelRadio.isChecked():
                    # Оставляем только синий канал
                    new_color = QColor(0, 0, b)
                elif self.grayscaleRadio.isChecked():
                    # Конвертация в оттенки серого
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    new_color = QColor(gray, gray, gray)
                else:
                    new_color = color

                image.setPixelColor(x, y, new_color)

        return QPixmap.fromImage(image)

    def rotate_image(self, angle):
        """Поворот изображения"""
        if self.current_pixmap:
            self.rotation_angle = (self.rotation_angle + angle) % 360
            self.update_image_display()

    def rotate_left(self):
        """Поворот на 90 градусов влево"""
        self.rotate_image(-90)
        self.statusbar.showMessage("Изображение повернуто на 90° влево")

    def rotate_right(self):
        """Поворот на 90 градусов вправо"""
        self.rotate_image(90)
        self.statusbar.showMessage("Изображение повернуто на 90° вправо")

    def reset_rotation(self):
        """Сброс поворота"""
        self.rotation_angle = 0
        self.update_image_display()
        self.statusbar.showMessage("Поворот сброшен")

    def update_image_display(self):
        """Обновление отображения изображения"""
        if self.current_pixmap is None:
            return

        try:
            # Применяем поворот
            transform = QTransform().rotate(self.rotation_angle)
            rotated_pixmap = self.current_pixmap.transformed(transform, Qt.SmoothTransformation)

            # Применяем цветовой канал
            processed_pixmap = self.apply_color_channel(rotated_pixmap)

            # Масштабирование для отображения с сохранением пропорций
            label_size = self.imageLabel.size()
            scaled_pixmap = processed_pixmap.scaled(
                label_size.width() - 20,
                label_size.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.imageLabel.setPixmap(scaled_pixmap)

        except Exception as e:
            self.show_error(f"Ошибка при обработке изображения: {str(e)}")

    def update_controls(self):
        """Обновление состояния элементов управления"""
        has_image = self.current_pixmap is not None
        self.originalRadio.setEnabled(has_image)
        self.redChannelRadio.setEnabled(has_image)
        self.greenChannelRadio.setEnabled(has_image)
        self.blueChannelRadio.setEnabled(has_image)
        self.grayscaleRadio.setEnabled(has_image)
        self.rotateLeftButton.setEnabled(has_image)
        self.rotateRightButton.setEnabled(has_image)
        self.resetRotationButton.setEnabled(has_image and self.rotation_angle != 0)

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)
        self.statusbar.showMessage(f"Ошибка: {message}")

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        self.update_image_display()


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = ImageEditor()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()