import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt


class NumberAnalyzer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('designer.ui', self)

        # Подключение кнопок к функциям
        self.loadButton.clicked.connect(self.load_file)
        self.saveButton.clicked.connect(self.save_results)

        # Переменные для хранения результатов
        self.min_value = None
        self.max_value = None
        self.avg_value = None
        self.numbers = []

        # Обновление интерфейса
        self.update_display()

    def load_file(self):
        """Загрузка файла и анализ чисел"""
        try:
            # Открытие диалога выбора файла
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите текстовый файл",
                "",
                "Text Files (*.txt);;All Files (*)"
            )

            if not file_path:
                return  # Пользователь отменил выбор

            # Чтение и анализ файла
            self.analyze_file(file_path)

        except Exception as e:
            self.show_error(f"Ошибка при загрузке файла: {str(e)}")

    def analyze_file(self, file_path):
        """Анализ чисел в файле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Разделение содержимого на числа (используем пробельные символы как разделители)
            number_strings = content.split()
            numbers = []

            # Преобразование строк в числа с обработкой ошибок
            for num_str in number_strings:
                try:
                    number = int(num_str)
                    numbers.append(number)
                except ValueError:
                    # Пропускаем нечисловые значения
                    continue

            if not numbers:
                self.show_error("В файле не найдено корректных целых чисел")
                return

            # Расчет статистики
            self.numbers = numbers
            self.min_value = min(numbers)
            self.max_value = max(numbers)
            self.avg_value = sum(numbers) / len(numbers)

            # Обновление интерфейса
            self.update_display()

            # Вывод информации о файле
            file_name = os.path.basename(file_path)
            self.statusTextEdit.setText(
                f"Файл '{file_name}' успешно загружен\n"
                f"Найдено чисел: {len(numbers)}\n"
                f"Нечисловые значения были проигнорированы"
            )

        except UnicodeDecodeError:
            self.show_error("Ошибка кодировки файла. Попробуйте файл в кодировке UTF-8")
        except Exception as e:
            self.show_error(f"Ошибка при анализе файла: {str(e)}")

    def save_results(self):
        """Сохранение результатов в файл"""
        if self.min_value is None or self.max_value is None or self.avg_value is None:
            self.show_error("Нет данных для сохранения. Сначала загрузите файл")
            return

        try:
            # Открытие диалога сохранения файла
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить результаты",
                "results.txt",
                "Text Files (*.txt);;All Files (*)"
            )

            if not file_path:
                return  # Пользователь отменил сохранение

            # Запись результатов в файл
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("Результаты анализа чисел:\n")
                file.write("=" * 30 + "\n")
                file.write(f"Минимальное значение: {self.min_value}\n")
                file.write(f"Максимальное значение: {self.max_value}\n")
                file.write(f"Среднее значение: {self.avg_value:.2f}\n")
                file.write(f"Количество чисел: {len(self.numbers)}\n")
                file.write("=" * 30 + "\n")

            # Вывод сообщения об успешном сохранении
            self.statusTextEdit.setText(f"Результаты сохранены в файл: {file_path}")

        except Exception as e:
            self.show_error(f"Ошибка при сохранении файла: {str(e)}")

    def update_display(self):
        """Обновление отображения результатов"""
        if self.min_value is not None:
            self.minValueLabel.setText(str(self.min_value))
            self.maxValueLabel.setText(str(self.max_value))
            self.avgValueLabel.setText(f"{self.avg_value:.2f}")
        else:
            self.minValueLabel.setText("Не рассчитано")
            self.maxValueLabel.setText("Не рассчитано")
            self.avgValueLabel.setText("Не рассчитано")

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)
        self.statusTextEdit.setText(f"Ошибка: {message}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = NumberAnalyzer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()