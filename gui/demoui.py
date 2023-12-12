import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import json
import random


class MatplotlibWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use("dark_background")
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        # Apply dark theme to Matplotlib
        self.plot()

    def plot(self):
        x = np.linspace(0, 5, 100)
        y = np.sin(x)
        self.ax.plot(x, y)
        self.ax.set_title("Matplotlib Example")
        # Apply dark theme to Matplotlib
        self.apply_dark_theme()

        self.draw()

    def apply_dark_theme(self):
        dark_palette = plt.rcParams.copy()
        dark_palette["axes.facecolor"] = "#333333"
        dark_palette["axes.edgecolor"] = "#ffffff"
        dark_palette["axes.labelcolor"] = "#ffffff"
        dark_palette["text.color"] = "#ffffff"
        dark_palette["xtick.color"] = "#ffffff"
        dark_palette["ytick.color"] = "#ffffff"
        dark_palette["grid.color"] = "#ffffff"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #333333;
                color: white;
                border: 1px solid white;
            }
                """
        )
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set window icon
        self.setWindowIcon(QIcon("assets/img/icon.png"))

        # Matplotlib widget
        self.canvas = MatplotlibWidget(self.central_widget)

        # List widget
        self.list1_label = QLabel("All Coins", self.central_widget)
        self.list1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list1_label.setStyleSheet("color: white; font-weight: bold;")
        self.list_view = QListView(self.central_widget)
        self.list_model = self.load_items_from_json("crypto_list.json")
        self.list_model = QStringListModel(self.list_model)
        self.list_view.setModel(self.list_model)
        self.list_view.doubleClicked.connect(self.on_list_item_double_clicked)

        # Second list widget with random data
        self.list2_label = QLabel("Open Orders", self.central_widget)
        self.list2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list2_label.setStyleSheet("color: white; font-weight: bold;")
        self.random_data = [
            "BTCUSDT",
            "XRPUSDT",
            "PEPEUSDT",
            "TRXUSDT",
        ]  # Özelleştirilebilir
        self.random_model = QStringListModel(self.random_data)
        self.random_list_view = QListView(self.central_widget)
        self.random_list_view.setModel(self.random_model)

        # Thirst list widget with temp data
        self.list3_label = QLabel("Scan Result", self.central_widget)
        self.list3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list3_label.setStyleSheet("color: white; font-weight: bold;")
        self.list3_data = [
            "BTCUSDT",
            "XRPUSDT",
            "PEPEUSDT",
            "TRXUSDT",
        ]
        self.list3_model = QStringListModel(self.list3_data)
        self.list3_list_view = QListView(self.central_widget)
        self.list3_list_view.setModel(self.list3_model)

        # Forth list widget with temp data
        self.list4_label = QLabel("Scan Result For Open Orders", self.central_widget)
        self.list4_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list4_label.setStyleSheet("color: white; font-weight: bold;")
        self.list4_data = [
            "BTCUSDT",
            "XRPUSDT",
            "PEPEUSDT",
            "TRXUSDT",
        ]
        self.list4_model = QStringListModel(self.list4_data)
        self.list4_list_view = QListView(self.central_widget)
        self.list4_list_view.setModel(self.list4_model)

        # Disable editing on double-click for the list view
        self.list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.random_list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.list3_list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.list4_list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Buttons
        self.button2 = QPushButton("Add Open Order", self.central_widget)
        self.button2.clicked.connect(self.on_button2_clicked)

        # Layout
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addWidget(self.canvas, 75)  # Matplotlib widget 70% of the width
        self.in_layout = QVBoxLayout()
        self.inner_layout = QVBoxLayout()
        self.in_layout.addWidget(self.list1_label)
        self.in_layout.addWidget(self.list_view)
        self.in_layout.addWidget(self.button2)
        self.in_layout.addWidget(self.list3_label)
        self.in_layout.addWidget(self.list3_list_view)
        self.inner_layout.addWidget(self.list2_label)
        self.inner_layout.addWidget(self.random_list_view)
        self.inner_layout.addWidget(self.list4_label)
        self.inner_layout.addWidget(self.list4_list_view)
        self.layout.addLayout(self.in_layout, 15)  # Inner layout 10% of the width
        self.layout.addLayout(self.inner_layout, 10)  # Inner layout 10% of the width

        # Set dark theme
        self.set_dark_theme()

        # Set window title
        self.setWindowTitle("Crypto Scan Basic Plan")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(53, 53, 53)
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Active,
            QPalette.ColorRole.WindowText,
            Qt.GlobalColor.white,
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(53, 53, 53)
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.WindowText,
            Qt.GlobalColor.white,
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(53, 53, 53)
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText,
            Qt.GlobalColor.white,
        )

        self.setPalette(dark_palette)
        self.setStyleSheet(
            "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }"
        )

        # Set button styles
        button_style = "QPushButton { background-color: #333333; color: #ffffff; border: 1px solid white; border-radius: 5px; padding: 5px; font-weight: bold; }"
        self.button2.setStyleSheet(button_style)

        # Set list style
        list_style = "QListView { background-color: #333333; color: #ffffff; border: 1px solid white; border-radius: 5px; padding: 5px; font-weight: bold; }"
        self.list_view.setStyleSheet(list_style)

        random_list_style = "QListView { background-color: #333333; color: #ffffff; border: 1px solid white; border-radius: 5px; padding: 5px; font-weight: bold; }"
        self.random_list_view.setStyleSheet(random_list_style)

        list3_list_style = "QListView { background-color: #333333; color: #ffffff; border: 1px solid white; border-radius: 5px; padding: 5px; font-weight: bold; }"
        self.list3_list_view.setStyleSheet(list3_list_style)

        list4_list_style = "QListView { background-color: #333333; color: #ffffff; border: 1px solid white; border-radius: 5px; padding: 5px; font-weight: bold; }"
        self.list4_list_view.setStyleSheet(list4_list_style)

        # Set font for buttons and list
        font = QFont()
        font.setBold(True)
        self.button2.setFont(font)
        self.list_view.setFont(font)

    def load_items_from_json(self, json_path):
        try:
            with open(json_path, "r") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error loading items from JSON: {e}")
            return []

    def on_button2_clicked(self):
        pass

    def on_list_item_double_clicked(self, index):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
