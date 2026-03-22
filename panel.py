from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QButtonGroup, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from constants import (
    BG_PANEL, BG_CARD, BORDER, BORDER_LIT,
    ACCENT, ACCENT2, SUCCESS, DANGER,
    TEXT, TEXT_DIM, TEXT_BRIGHT,
    START, END, WALL, VISITED, FRONTIER, PATH,
)
from grid import Grid


# Reusable styled widgets

class Separator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {BORDER.name()}; border: none;")


class SectionLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text.upper())
        self.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
        self.setStyleSheet(f"""
            color: {ACCENT.name()};
            letter-spacing: 4px;
            padding: 0 2px;
            background: transparent;
            border: none;
        """)


class RadioButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setCheckable(True)
        self.setFont(QFont("Courier New", 9))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        r, g, b = ACCENT.red(), ACCENT.green(), ACCENT.blue()
        self.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD.name()};
                border: 1px solid {BORDER.name()};
                color: {TEXT_DIM.name()};
                padding: 7px 12px;
                text-align: left;
                border-radius: 5px;
                font-size: 9pt;
                letter-spacing: 0.5px;
            }}
            QPushButton:checked {{
                background: rgba({r},{g},{b}, 18);
                border: 1px solid rgba({r},{g},{b}, 200);
                color: rgba({r},{g},{b}, 255);
                font-weight: bold;
            }}
            QPushButton:hover:!checked {{
                background: rgba({r},{g},{b}, 8);
                border: 1px solid {BORDER_LIT.name()};
                color: {TEXT.name()};
            }}
        """)


class ActionButton(QPushButton):
    def __init__(self, text: str, color: QColor, slot, primary: bool = False):
        super().__init__(text)
        self.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(slot)
        r, g, b = color.red(), color.green(), color.blue()
        border_w = 2 if primary else 1
        pad = "10" if primary else "7"
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba({r},{g},{b}, 15);
                border: {border_w}px solid rgba({r},{g},{b}, 140);
                color: rgba({r},{g},{b}, 210);
                padding: {pad}px 12px;
                border-radius: 5px;
                letter-spacing: 2px;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background: rgba({r},{g},{b}, 40);
                border: {border_w}px solid rgba({r},{g},{b}, 255);
                color: rgb({r},{g},{b});
            }}
            QPushButton:pressed {{
                background: rgba({r},{g},{b}, 65);
            }}
        """)


class LegendRow(QWidget):
    def __init__(self, label: str, color: QColor):
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(10)

        r, g, b = color.red(), color.green(), color.blue()
        swatch = QLabel()
        swatch.setFixedSize(12, 12)
        swatch.setStyleSheet(f"""
            background: rgba({r},{g},{b}, 30);
            border-radius: 2px;
            border: 1px solid rgba({r},{g},{b}, 180);
        """)

        lbl = QLabel(label)
        lbl.setFont(QFont("Courier New", 8))
        lbl.setStyleSheet(f"color: {TEXT_DIM.name()}; background: transparent; border: none;")

        layout.addWidget(swatch)
        layout.addWidget(lbl)
        layout.addStretch()


class Card(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_CARD.name()};
                border: 1px solid {BORDER.name()};
                border-radius: 6px;
            }}
        """)

    def with_layout(self, spacing=5, margins=(8, 8, 8, 8)):
        layout = QVBoxLayout(self)
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout


# Main Panel

class Panel(QWidget):
    def __init__(self, grid: Grid):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_PANEL.name()};
                border-right: 1px solid {BORDER.name()};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 22, 14, 20)
        root.setSpacing(0)

        # Header 
        header = QWidget()
        header.setStyleSheet("border: none; background: transparent;")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(2, 0, 0, 0)
        hl.setSpacing(3)

        title = QLabel("PATHFINDER")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {ACCENT.name()};
            letter-spacing: 5px;
            border: none;
            background: transparent;
        """)

        sub = QLabel("graph search visualizer")
        sub.setFont(QFont("Courier New", 7))
        sub.setStyleSheet(f"""
            color: {TEXT_DIM.name()};
            letter-spacing: 1px;
            border: none;
            background: transparent;
        """)

        hl.addWidget(title)
        hl.addWidget(sub)
        root.addWidget(header)
        root.addSpacing(18)

        # Algorithm 
        root.addWidget(SectionLabel("Algorithm"))
        root.addSpacing(5)
        algo_card = Card()
        al = algo_card.with_layout()
        self.algo_group = QButtonGroup(self)
        for i, (label, key, tip) in enumerate([
            ("BFS",  "bfs",   "Breadth-first — shortest path"),
            ("DFS",  "dfs",   "Depth-first — exploratory"),
            ("A*",   "astar", "Heuristic — fastest route"),
        ]):
            btn = RadioButton(label)
            btn.setProperty("algo", key)
            btn.setToolTip(tip)
            self.algo_group.addButton(btn, i)
            al.addWidget(btn)
            if key == "bfs":
                btn.setChecked(True)
        self.algo_group.buttonClicked.connect(
            lambda b: setattr(grid, "algorithm", b.property("algo"))
        )
        root.addWidget(algo_card)
        root.addSpacing(12)

        # Draw Mode 
        root.addWidget(SectionLabel("Draw Mode"))
        root.addSpacing(5)
        mode_card = Card()
        ml = mode_card.with_layout()
        self.mode_group = QButtonGroup(self)
        for i, (label, key) in enumerate([
            ("▪  Wall",       "wall"),
            ("◈  Start (S)",  "start"),
            ("◇  End (E)",    "end"),
        ]):
            btn = RadioButton(label)
            btn.setProperty("mode", key)
            self.mode_group.addButton(btn, i)
            ml.addWidget(btn)
            if key == "wall":
                btn.setChecked(True)
        self.mode_group.buttonClicked.connect(
            lambda b: setattr(grid, "mode", b.property("mode"))
        )
        root.addWidget(mode_card)
        root.addSpacing(14)

        # Actions 
        root.addWidget(ActionButton("▶   EXECUTE",     ACCENT,           grid.run,        primary=True))
        root.addSpacing(5)
        root.addWidget(ActionButton("↺   CLEAR PATH",  QColor("#3a4a6a"), grid.clear_path))
        root.addSpacing(4)
        root.addWidget(ActionButton("✕   CLEAR ALL",   ACCENT2,          grid.clear_all))
        root.addSpacing(16)

        # Legend 
        root.addWidget(SectionLabel("Legend"))
        root.addSpacing(5)
        legend_card = Card()
        ll = legend_card.with_layout(spacing=2, margins=(8, 7, 8, 7))
        for label, color in [
            ("Start",    START),
            ("End",      END),
            ("Wall",     WALL),
            ("Visited",  VISITED),
            ("Frontier", FRONTIER),
            ("Path",     PATH),
        ]:
            ll.addWidget(LegendRow(label, color))
        root.addWidget(legend_card)

        root.addStretch()

        # Status
        root.addWidget(Separator())
        root.addSpacing(10)

        self.status = QLabel("> ready_")
        self.status.setFont(QFont("Courier New", 8))
        self.status.setStyleSheet(f"""
            color: {TEXT_DIM.name()};
            padding: 2px;
            border: none;
            background: transparent;
        """)
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        grid.status_changed.connect(self._on_status)

    def _on_status(self, msg: str):
        if "✓" in msg or "Done" in msg:
            color = SUCCESS.name()
        elif "✕" in msg or "⚠" in msg or "No path" in msg:
            color = DANGER.name()
        elif "Running" in msg:
            color = ACCENT.name()
        else:
            color = TEXT_DIM.name()

        self.status.setStyleSheet(f"""
            color: {color};
            padding: 2px;
            border: none;
            background: transparent;
        """)
        self.status.setText(f"> {msg}_")