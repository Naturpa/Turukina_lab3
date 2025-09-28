import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor


class TextEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('text_editor.ui', self)

        # Текущий файл
        self.current_file = None
        self.is_modified = False

        # Подключение кнопок к функциям
        self.newButton.clicked.connect(self.new_file)
        self.openButton.clicked.connect(self.open_file)
        self.saveButton.clicked.connect(self.save_file)

        # Подключение действий меню
        self.actionNew.triggered.connect(self.new_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionExit.triggered.connect(self.close)

        # Подключение сигнала изменения текста
        self.textEdit.textChanged.connect(self.text_modified)

        # Обновление интерфейса
        self.update_title()

    def new_file(self):
        """Создание нового файла"""
        if self.check_save():
            self.textEdit.clear()
            self.current_file = None
            self.is_modified = False
            self.fileNameLabel.setText("Новый файл")
            self.update_title()
            self.statusbar.showMessage("Создан новый файл")

    def open_file(self):
        """Открытие файла"""
        if self.check_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Открыть файл",
                "",
                "Text Files (*.txt);;All Files (*)"
            )

            if file_path:
                self.load_file(file_path)

    def load_file(self, file_path):
        """Загрузка файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.textEdit.setPlainText(content)
            self.current_file = file_path
            self.is_modified = False

            # Обновление интерфейса
            file_name = os.path.basename(file_path)
            self.fileNameLabel.setText(file_name)
            self.update_title()
            self.statusbar.showMessage(f"Файл открыт: {file_path}")

        except UnicodeDecodeError:
            # Попробуем другие кодировки
            try:
                with open(file_path, 'r', encoding='cp1251') as file:
                    content = file.read()

                self.textEdit.setPlainText(content)
                self.current_file = file_path
                self.is_modified = False
                file_name = os.path.basename(file_path)
                self.fileNameLabel.setText(file_name)
                self.update_title()
                self.statusbar.showMessage(f"Файл открыт (кодировка Windows-1251): {file_path}")

            except Exception as e:
                self.show_error(f"Ошибка при открытии файла: {str(e)}")

        except Exception as e:
            self.show_error(f"Ошибка при открытии файла: {str(e)}")

    def save_file(self):
        """Сохранение файла"""
        if self.current_file:
            # Сохраняем в текущий файл
            self.save_to_file(self.current_file)
        else:
            # Сохраняем как новый файл
            self.save_file_as()

    def save_file_as(self):
        """Сохранение файла с выбором имени"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            self.save_to_file(file_path)
            return True
        return False

    def save_to_file(self, file_path):
        """Сохранение содержимого в файл"""
        try:
            content = self.textEdit.toPlainText()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            self.current_file = file_path
            self.is_modified = False

            # Обновление интерфейса
            file_name = os.path.basename(file_path)
            self.fileNameLabel.setText(file_name)
            self.update_title()
            self.statusbar.showMessage(f"Файл сохранен: {file_path}")

            return True

        except Exception as e:
            self.show_error(f"Ошибка при сохранении файла: {str(e)}")
            return False

    def text_modified(self):
        """Обработчик изменения текста"""
        if not self.is_modified:
            self.is_modified = True
            self.update_title()

    def check_save(self):
        """Проверка необходимости сохранения перед действием"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Сохранение файла",
                "Документ был изменен. Сохранить изменения?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                return self.save_file()
            elif reply == QMessageBox.Cancel:
                return False

        return True

    def update_title(self):
        """Обновление заголовка окна"""
        if self.current_file:
            file_name = os.path.basename(self.current_file)
        else:
            file_name = "Новый файл"

        if self.is_modified:
            title = f"{file_name} * - Текстовый редактор"
        else:
            title = f"{file_name} - Текстовый редактор"

        self.setWindowTitle(title)

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)
        self.statusbar.showMessage(f"Ошибка: {message}")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = TextEditor()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()