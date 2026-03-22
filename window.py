from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from constants import BG
from grid import Grid
from panel import Panel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pathfinder Visualizer")
        self.setStyleSheet(f"background: {BG.name()};")

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        grid  = Grid()
        panel = Panel(grid)

        layout.addWidget(panel)
        layout.addWidget(grid)

        self.showMaximized()