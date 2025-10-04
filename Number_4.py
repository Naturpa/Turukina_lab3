import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter


class AlphaImageEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('alpha_editor.ui', self)

        # Инициализация переменных
        self.original_pixmap = None
        self.current_alpha = 100  # 100% - полностью непрозрачное

        # Подключение сигналов
        self.loadButton.clicked.connect(self.load_image)
        self.alphaSlider.valueChanged.connect(self.slider_changed)

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

                # Сохранение оригинального изображения
                self.original_pixmap = pixmap
                self.current_alpha = 100

                # Сброс слайдера к 100%
                self.alphaSlider.setValue(100)

                # Обновление интерфейса
                file_name = os.path.basename(file_path)
                self.fileNameLabel.setText(f"Загружено: {file_name}")
                self.update_image_display()
                self.update_controls()

                self.statusbar.showMessage(f"Изображение загружено: {file_name}")

            except Exception as e:
                self.show_error(f"Ошибка при загрузке изображения: {str(e)}")

    def apply_alpha_channel(self, pixmap, alpha):
        """Применение альфа-канала к изображению"""
        if pixmap is None:
            return None

        # Создаем прозрачное изображение того же размера
        transparent_pixmap = QPixmap(pixmap.size())
        transparent_pixmap.fill(Qt.transparent)

        # Создаем QPainter для рисования на прозрачном pixmap
        painter = QPainter(transparent_pixmap)

        # Устанавливаем непрозрачность (альфа-канал)
        painter.setOpacity(alpha / 100.0)

        # Рисуем оригинальное изображение
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return transparent_pixmap

    def slider_changed(self, value):
        """Обработчик изменения положения слайдера"""
        self.current_alpha = value
        self.alphaValueLabel.setText(f"{value}%")
        self.update_image_display()
        self.statusbar.showMessage(f"Прозрачность установлена: {value}%")

    def update_image_display(self):
        """Обновление отображения изображения"""
        if self.original_pixmap is None:
            return

        try:
            # Применяем альфа-канал
            transparent_pixmap = self.apply_alpha_channel(
                self.original_pixmap,
                self.current_alpha
            )

            if transparent_pixmap:
                # Масштабирование для отображения с сохранением пропорций
                label_size = self.imageLabel.size()
                scaled_pixmap = transparent_pixmap.scaled(
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
        has_image = self.original_pixmap is not None
        self.alphaSlider.setEnabled(has_image)

        if not has_image:
            self.alphaValueLabel.setText("100%")
            self.alphaSlider.setValue(100)

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

    window = AlphaImageEditor()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
