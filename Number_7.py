import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import random


class PianoKey(QtWidgets.QPushButton):
    def __init__(self, note, is_black=False, parent=None):
        super().__init__(parent)
        self.note = note
        self.is_black = is_black

        # Настройка внешнего вида клавиши
        if is_black:
            self.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 0px 0px 4px 4px;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)
            self.setFixedSize(30, 120)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 0px 0px 4px 4px;
                }
                QPushButton:pressed {
                    background-color: #ddd;
                }
            """)
            self.setFixedSize(40, 180)

        self.setText(note)


class PianoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keys = []
        self.sounds = {}
        self.player = QMediaPlayer()
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создание клавиш пианино (одна октава)
        white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_notes = ['C#', 'D#', '', 'F#', 'G#', 'A#', '']

        for i, (white_note, black_note) in enumerate(zip(white_notes, black_notes)):
            # Белая клавиша
            white_key = PianoKey(white_note, False)
            white_key.clicked.connect(lambda checked, note=white_note: self.play_note(note))
            layout.addWidget(white_key)
            self.keys.append(white_key)

            # Черная клавиша (если есть)
            if black_note:
                black_key = PianoKey(black_note, True)
                black_key.clicked.connect(lambda checked, note=black_note: self.play_note(note))

                # Позиционируем черную клавишу поверх белых
                black_key.move(white_key.x() + 25, 0)
                self.keys.append(black_key)

        self.setLayout(layout)

    def load_sounds(self, sound_files):
        """Загрузка звуковых файлов"""
        self.sounds = sound_files
        self.player = QMediaPlayer()

    def play_note(self, note):
        """Проигрывание ноты"""
        if note in self.sounds:
            media_content = QMediaContent(QUrl.fromLocalFile(self.sounds[note]))
            self.player.setMedia(media_content)
            self.player.play()

    def play_notes_sequence(self, notes, delay=500):
        """Проигрывание последовательности нот"""
        self.current_melody = notes
        self.current_note_index = 0
        self.melody_timer = QTimer()
        self.melody_timer.timeout.connect(self.play_next_note)
        self.melody_timer.start(delay)

    def play_next_note(self):
        """Проигрывание следующей ноты в мелодии"""
        if self.current_note_index < len(self.current_melody):
            note = self.current_melody[self.current_note_index]
            self.play_note(note)
            self.current_note_index += 1
        else:
            self.melody_timer.stop()

    def stop_playback(self):
        """Остановка проигрывания"""
        if hasattr(self, 'melody_timer') and self.melody_timer.isActive():
            self.melody_timer.stop()
        self.player.stop()


class PianoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('piano.ui', self)

        # Инициализация переменных
        self.sounds_loaded = False
        self.sound_files = {}

        # Создание и настройка виджета пианино
        self.piano_widget = PianoWidget()
        piano_layout = QtWidgets.QVBoxLayout()
        piano_layout.addWidget(self.piano_widget)
        self.pianoWidget.setLayout(piano_layout)

        # Подключение сигналов
        self.loadSoundsButton.clicked.connect(self.load_sounds)
        self.melody1Button.clicked.connect(self.play_melody1)
        self.melody2Button.clicked.connect(self.play_melody2)
        self.melody3Button.clicked.connect(self.play_melody3)
        self.stopButton.clicked.connect(self.stop_playback)

        # Обновление интерфейса
        self.update_controls()

        self.statusbar.showMessage("Готов к работе. Загрузите звуковые файлы.")

    def load_sounds(self):
        """Загрузка звуковых файлов"""
        sound_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку со звуками нот",
            "",
            QFileDialog.ShowDirsOnly
        )

        if sound_dir:
            try:
                # Ожидаемые названия файлов для одной октавы
                expected_files = {
                    'C': ['c4.wav', 'c4.mp3', 'C.wav', 'C.mp3'],
                    'C#': ['c#4.wav', 'c#4.mp3', 'C#.wav', 'C#.mp3', 'db4.wav', 'db4.mp3'],
                    'D': ['d4.wav', 'd4.mp3', 'D.wav', 'D.mp3'],
                    'D#': ['d#4.wav', 'd#4.mp3', 'D#.wav', 'D#.mp3', 'eb4.wav', 'eb4.mp3'],
                    'E': ['e4.wav', 'e4.mp3', 'E.wav', 'E.mp3'],
                    'F': ['f4.wav', 'f4.mp3', 'F.wav', 'F.mp3'],
                    'F#': ['f#4.wav', 'f#4.mp3', 'F#.wav', 'F#.mp3', 'gb4.wav', 'gb4.mp3'],
                    'G': ['g4.wav', 'g4.mp3', 'G.wav', 'G.mp3'],
                    'G#': ['g#4.wav', 'g#4.mp3', 'G#.wav', 'G#.mp3', 'ab4.wav', 'ab4.mp3'],
                    'A': ['a4.wav', 'a4.mp3', 'A.wav', 'A.mp3'],
                    'A#': ['a#4.wav', 'a#4.mp3', 'A#.wav', 'A#.mp3', 'bb4.wav', 'bb4.mp3'],
                    'B': ['b4.wav', 'b4.mp3', 'B.wav', 'B.mp3']
                }

                loaded_count = 0
                self.sound_files = {}

                # Поиск файлов для каждой ноты
                for note, possible_filenames in expected_files.items():
                    for filename in possible_filenames:
                        file_path = os.path.join(sound_dir, filename)
                        if os.path.exists(file_path):
                            self.sound_files[note] = file_path
                            loaded_count += 1
                            break

                if loaded_count > 0:
                    self.sounds_loaded = True
                    self.piano_widget.load_sounds(self.sound_files)
                    self.statusLabel.setText(f"Загружено звуков: {loaded_count}/12")
                    self.statusbar.showMessage(f"Успешно загружено {loaded_count} звуковых файлов")

                    # Включение кнопок мелодий если загружено достаточно звуков
                    self.update_controls()

                else:
                    self.show_error("Не найдено подходящих звуковых файлов")

            except Exception as e:
                self.show_error(f"Ошибка при загрузке звуков: {str(e)}")

    def play_melody1(self):
        """Проигрывание мелодии 'До-Ре-Ми'"""
        if self.sounds_loaded:
            melody = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
            self.piano_widget.play_notes_sequence(melody, 400)
            self.statusbar.showMessage("Играет: До-Ре-Ми")

    def play_melody2(self):
        """Проигрывание мелодии 'Маленькая ёлочка'"""
        if self.sounds_loaded:
            melody = ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'G', 'C', 'D', 'E']
            self.piano_widget.play_notes_sequence(melody, 300)
            self.statusbar.showMessage("Играет: Маленькая ёлочка")

    def play_melody3(self):
        """Проигрывание случайной мелодии"""
        if self.sounds_loaded:
            notes = list(self.sound_files.keys())
            melody = [random.choice(notes) for _ in range(8)]
            self.piano_widget.play_notes_sequence(melody, 200)
            self.statusbar.showMessage("Играет: Случайная мелодия")

    def stop_playback(self):
        """Остановка проигрывания"""
        self.piano_widget.stop_playback()
        self.statusbar.showMessage("Воспроизведение остановлено")

    def update_controls(self):
        """Обновление состояния элементов управления"""
        self.melody1Button.setEnabled(self.sounds_loaded)
        self.melody2Button.setEnabled(self.sounds_loaded)
        self.melody3Button.setEnabled(self.sounds_loaded)
        self.stopButton.setEnabled(self.sounds_loaded)

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)
        self.statusbar.showMessage(f"Ошибка: {message}")


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = PianoApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()