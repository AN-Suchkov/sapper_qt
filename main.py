import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QPushButton,
                             QLCDNumber, QLabel, QSpinBox, QSizePolicy, QButtonGroup,
                             QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QRect, QSize, Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QFont, QPixmap, QKeyEvent
import os


class GameLogic:
    def __init__(self, grid_size=10, num_mines=15):
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.field = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.list_mines = []
        self.opened_cells = set()
        self.flagged_cells = set()
        self.empty = grid_size * grid_size - num_mines
        self.first_click = True

    def generate_mines(self, first_x, first_y):
        """Генерация мин, исключая первую клетку и её соседей"""
        safe_zone = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    safe_zone.add((nx, ny))

        self.list_mines = []
        while len(self.list_mines) < self.num_mines:
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if (x, y) not in safe_zone and (x, y) not in self.list_mines:
                self.list_mines.append((x, y))
                self.field[y][x] = 'mine'

        # Обновляем числа для всех клеток
        self.update_numbers()

    def update_numbers(self):
        """Обновление чисел на поле после расстановки мин"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.field[y][x] != 'mine':
                    self.field[y][x] = self.count_adjacent_mines(x, y)

    def count_adjacent_mines(self, x, y):
        """Подсчет мин вокруг клетки"""
        mines_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if self.field[ny][nx] == 'mine':
                        mines_count += 1
        return mines_count

    def reveal_cell(self, x, y):
        """Открытие клетки и рекурсивное открытие пустых клеток"""
        if self.first_click:
            self.generate_mines(x, y)
            self.first_click = False

        if (x, y) in self.opened_cells or (x, y) in self.flagged_cells:
            return set()

        self.opened_cells.add((x, y))
        cells_to_reveal = {(x, y)}

        if self.field[y][x] == 'mine':
            return cells_to_reveal

        self.empty -= 1

        if self.field[y][x] == 0:
            # Рекурсивно открываем соседей для пустых клеток
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        if (nx, ny) not in self.opened_cells and (nx, ny) not in self.flagged_cells:
                            cells_to_reveal.update(self.reveal_cell(nx, ny))

        return cells_to_reveal

    def toggle_flag(self, x, y):
        """Установка или снятие флага"""
        if (x, y) in self.opened_cells:
            return False

        if (x, y) in self.flagged_cells:
            self.flagged_cells.remove((x, y))
            return False
        else:
            self.flagged_cells.add((x, y))
            return True


class GameStats:
    def __init__(self, filename='stat.txt'):
        self.filename = filename
        self.wins = 0
        self.defeats = 0
        self.load_stats()

    def load_stats(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = f.read().split(';')
                    if len(data) >= 2:
                        self.wins = int(data[0])
                        self.defeats = int(data[1])
        except Exception as e:
            print(f"Error loading stats: {e}")

    def save_stats(self):
        try:
            with open(self.filename, 'w') as f:
                f.write(f'{self.wins};{self.defeats}')
        except Exception as e:
            print(f"Error saving stats: {e}")

    def increment_wins(self):
        self.wins += 1
        self.save_stats()

    def increment_defeats(self):
        self.defeats += 1
        self.save_stats()


class ResultsDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.set_message(message)

    def setup_ui(self):
        self.setFixedSize(300, 150)
        self.setWindowTitle("Game Result")

        layout = QVBoxLayout()

        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.text_label)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def set_message(self, message):
        self.text_label.setText(message)


class CustomFieldDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(300, 200)
        self.setWindowTitle("Custom Field")

        layout = QVBoxLayout()

        # Размер поля
        size_layout = QHBoxLayout()
        self.size_label = QLabel("Field Size:")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setMinimum(5)
        self.size_spinbox.setMaximum(30)
        self.size_spinbox.setValue(10)
        size_layout.addWidget(self.size_label)
        size_layout.addWidget(self.size_spinbox)
        layout.addLayout(size_layout)

        # Количество мин
        mines_layout = QHBoxLayout()
        self.mines_label = QLabel("Mines:")
        self.mines_spinbox = QSpinBox()
        self.mines_spinbox.setMinimum(1)
        self.mines_spinbox.setMaximum(100)
        self.mines_spinbox.setValue(15)
        mines_layout.addWidget(self.mines_label)
        mines_layout.addWidget(self.mines_spinbox)
        layout.addLayout(mines_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_values(self):
        return self.size_spinbox.value(), self.mines_spinbox.value()


class SettingsDialog(QDialog):
    def __init__(self, game_stats, parent=None):
        super().__init__(parent)
        self.game_stats = game_stats
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(300, 200)
        self.setWindowTitle("Settings")

        layout = QVBoxLayout()

        # Статистика
        stats_layout = QHBoxLayout()
        self.wins_label = QLabel(f"Wins: {self.game_stats.wins}")
        self.defeats_label = QLabel(f"Defeats: {self.game_stats.defeats}")
        stats_layout.addWidget(self.wins_label)
        stats_layout.addWidget(self.defeats_label)
        layout.addLayout(stats_layout)

        # Кнопка сброса статистики
        self.reset_stats_button = QPushButton("Reset Statistics")
        self.reset_stats_button.clicked.connect(self.reset_stats)
        layout.addWidget(self.reset_stats_button)

        # Кнопка кастомного поля
        self.custom_field_button = QPushButton("Custom Field")
        self.custom_field_button.clicked.connect(self.open_custom_field)
        layout.addWidget(self.custom_field_button)

        # Кнопка закрытия
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def reset_stats(self):
        reply = QMessageBox.question(self, "Reset Statistics",
                                     "Are you sure you want to reset statistics?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.game_stats.wins = 0
            self.game_stats.defeats = 0
            self.game_stats.save_stats()
            self.wins_label.setText("Wins: 0")
            self.defeats_label.setText("Defeats: 0")

    def open_custom_field(self):
        self.custom_dialog = CustomFieldDialog(self)
        if self.custom_dialog.exec_() == QDialog.Accepted:
            size, mines = self.custom_dialog.get_values()
            self.parent().start_custom_game(size, mines)
            self.close()


class MainGameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_stats = GameStats()
        self.grid_size = 10
        self.num_mines = 15
        self.init_ui()
        self.start_new_game()

    def init_ui(self):
        self.setWindowTitle('Minesweeper')
        self.setFixedSize(600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Создаем панель управления
        self.create_control_panel()

        # Создаем контейнер для игрового поля
        self.field_container = QWidget()
        self.field_layout = QGridLayout()
        self.field_container.setLayout(self.field_layout)
        self.main_layout.addWidget(self.field_container)

    def create_control_panel(self):
        control_layout = QHBoxLayout()

        self.mines_counter = QLCDNumber()
        self.mines_counter.setDigitCount(3)
        control_layout.addWidget(self.mines_counter)

        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.show_settings)
        control_layout.addWidget(self.settings_button)

        self.mode_button = QPushButton('Reveal Mode')
        self.mode_button.clicked.connect(self.toggle_mode)
        control_layout.addWidget(self.mode_button)

        self.restart_button = QPushButton('Restart')
        self.restart_button.clicked.connect(self.start_new_game)
        control_layout.addWidget(self.restart_button)

        self.main_layout.addLayout(control_layout)

    def create_game_field(self):
        # Очищаем предыдущее поле
        for i in reversed(range(self.field_layout.count())):
            self.field_layout.itemAt(i).widget().setParent(None)

        self.buttons = {}
        button_size = max(30, 400 // self.grid_size)  # Адаптивный размер кнопок

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                button = QPushButton()
                button.setFixedSize(button_size, button_size)
                button.setObjectName(f"x{col}y{row}")
                button.clicked.connect(self.handle_click)
                self.buttons[(col, row)] = button
                self.field_layout.addWidget(button, row, col)

        # Обновляем размер окна
        field_width = self.grid_size * (button_size + 2) + 20
        field_height = self.grid_size * (button_size + 2) + 100
        self.setFixedSize(field_width, field_height)

    def start_new_game(self):
        self.game_logic = GameLogic(self.grid_size, self.num_mines)
        self.tap_mode = 1  # 1 for reveal, 0 for flag
        self.mode_button.setText("Reveal Mode")
        self.mines_counter.display(self.game_logic.num_mines)
        self.create_game_field()

    def start_custom_game(self, size, mines):
        # Проверяем, что количество мин не превышает размер поля
        max_mines = size * size - 9  # Оставляем как минимум 9 безопасных клеток
        if mines > max_mines:
            mines = max_mines
            QMessageBox.warning(self, "Too Many Mines",
                                f"Reduced mines to {mines} to ensure playability.")

        self.grid_size = size
        self.num_mines = mines
        self.start_new_game()

    def toggle_mode(self):
        self.tap_mode = 1 - self.tap_mode  # Переключаем режим
        self.mode_button.setText("Flag Mode" if self.tap_mode == 0 else "Reveal Mode")

    def keyPressEvent(self, event):
        # Обработка нажатия пробела для переключения режима
        if event.key() == Qt.Key_M:
            self.toggle_mode()
        super().keyPressEvent(event)

    def show_settings(self):
        settings_dialog = SettingsDialog(self.game_stats, self)
        settings_dialog.exec_()

    def handle_click(self):
        sender = self.sender()
        coords = tuple(map(int, sender.objectName()[1:].split('y')))

        if self.tap_mode == 1:  # Reveal mode
            self.reveal_cell(coords)
        else:  # Flag mode
            self.flag_cell(coords)

    def reveal_cell(self, coords):
        cells_to_reveal = self.game_logic.reveal_cell(*coords)

        for cell_coords in cells_to_reveal:
            x, y = cell_coords
            button = self.buttons[cell_coords]
            button.setEnabled(False)

            if self.game_logic.field[y][x] == 'mine':
                button.setStyleSheet('background-color: red;')
                self.defeat()
                return
            elif self.game_logic.field[y][x] > 0:
                button.setText(str(self.game_logic.field[y][x]))
                # Устанавливаем разные цвета для разных чисел
                colors = ['blue', 'green', 'red', 'darkblue', 'brown', 'cyan', 'black', 'gray']
                if self.game_logic.field[y][x] <= len(colors):
                    button.setStyleSheet(f'color: {colors[self.game_logic.field[y][x] - 1]}; font-weight: bold;')

        if self.game_logic.empty == 0:
            self.victory()

    def flag_cell(self, coords):
        x, y = coords
        is_flagged = self.game_logic.toggle_flag(x, y)
        button = self.buttons[coords]

        if is_flagged:
            button.setText('🚩')
            self.mines_counter.display(self.mines_counter.intValue() - 1)
        else:
            button.setText('')
            self.mines_counter.display(self.mines_counter.intValue() + 1)

    def defeat(self):
        # Показываем все мины
        for x, y in self.game_logic.list_mines:
            if (x, y) not in self.game_logic.flagged_cells:
                button = self.buttons[(x, y)]
                button.setStyleSheet('background-color: red;')

        result_dialog = ResultsDialog("YOU LOST :(", self)
        self.game_stats.increment_defeats()
        result_dialog.exec_()

    def victory(self):
        result_dialog = ResultsDialog("YOU WON!", self)
        self.game_stats.increment_wins()
        result_dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = MainGameWindow()
    game.show()
    sys.exit(app.exec_())