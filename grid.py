import heapq
from collections import deque

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QPen, QFont, QColor, QRadialGradient, QLinearGradient, QBrush

from constants import (
    GRID_LINE, EMPTY, WALL, START, END, VISITED, FRONTIER, PATH, BG,
    ACCENT,
    ROWS, COLS,
    EMPTY_S, WALL_S, START_S, END_S, VISITED_S, FRONTIER_S, PATH_S,
)


class Grid(QWidget):
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.rows = ROWS
        self.cols = COLS
        self.cells = [[EMPTY_S] * self.cols for _ in range(self.rows)]
        self.start = None
        self.end   = None

        self.mode      = "wall"
        self.algorithm = "bfs"
        self.running   = False
        self.draw_mode = None

        self.anim_steps  = []
        self.anim_index  = 0
        self._last_cell  = None
        self.timer       = QTimer()
        self.timer.timeout.connect(self._step)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    @property
    def cell_size(self):
        cw = self.width()  // self.cols
        ch = self.height() // self.rows
        return max(4, min(cw, ch))

    def paintEvent(self, _):
        p  = QPainter(self)
        cs = self.cell_size
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        gap    = max(1, cs // 12)
        radius = max(2, cs // 6)

        p.fillRect(self.rect(), GRID_LINE)

        for r in range(self.rows):
            for c in range(self.cols):
                state = self.cells[r][c]
                rect  = QRectF(c * cs + gap, r * cs + gap,
                               cs - gap * 2, cs - gap * 2)
                self._draw_cell(p, rect, state, radius, cs)

        if self.start:
            self._draw_label(p, self.start, "S", cs, START)
        if self.end:
            self._draw_label(p, self.end, "E", cs, END)

    @staticmethod
    def _glow(color: QColor, alpha: int) -> QColor:
        g = QColor(color)
        g.setAlpha(alpha)
        return g

    @staticmethod
    def _darker(color: QColor, by: int = 80) -> QColor:
        d = QColor(color)
        d.setRed(max(0, d.red()   - by))
        d.setGreen(max(0, d.green() - by))
        d.setBlue(max(0, d.blue()  - by))
        return d

    def _draw_cell(self, p: QPainter, rect: QRectF, state: int,
                   radius: int, cs: int):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        if state == EMPTY_S:
            self._draw_empty(p, rect, radius, cs)
        elif state == WALL_S:
            self._draw_wall(p, rect, radius)
        else:
            neon_map = {
                START_S:    START,
                END_S:      END,
                VISITED_S:  VISITED,
                FRONTIER_S: FRONTIER,
                PATH_S:     PATH,
            }
            self._draw_neon(p, rect, radius, neon_map[state], state)

    def _draw_empty(self, p: QPainter, rect: QRectF, radius: int, cs: int):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(EMPTY))
        p.drawRoundedRect(rect, radius, radius)

        tick = max(2, cs // 8)
        pen  = QPen(self._glow(ACCENT, 28), 1)
        p.setPen(pen)
        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()
        from PyQt6.QtCore import QLineF
        # top-left
        p.drawLine(QLineF(x, y, x + tick, y))
        p.drawLine(QLineF(x, y, x, y + tick))
        # top-right
        p.drawLine(QLineF(x + w - tick, y, x + w, y))
        p.drawLine(QLineF(x + w, y, x + w, y + tick))
        # bottom-left
        p.drawLine(QLineF(x, y + h, x + tick, y + h))
        p.drawLine(QLineF(x, y + h - tick, x, y + h))
        # bottom-right
        p.drawLine(QLineF(x + w - tick, y + h, x + w, y + h))
        p.drawLine(QLineF(x + w, y + h - tick, x + w, y + h))
        p.setPen(Qt.PenStyle.NoPen)

    def _draw_wall(self, p: QPainter, rect: QRectF, radius: int):
        """Wall: cool gunmetal gradient + scanlines + dim neon border."""
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor("#1e2440"))
        grad.setColorAt(0.5, QColor("#111626"))
        grad.setColorAt(1.0, QColor("#080b14"))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(rect, radius, radius)

        p.setPen(Qt.PenStyle.NoPen)
        scan = QColor("#000000")
        scan.setAlpha(35)
        p.setBrush(QBrush(scan))
        y = rect.y()
        while y < rect.y() + rect.height():
            line = QRectF(rect.x(), y, rect.width(), 1)
            p.fillRect(line, scan)
            y += 3

        border_c = self._glow(ACCENT, 45)
        p.setPen(QPen(border_c, 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
        p.setPen(Qt.PenStyle.NoPen)

    def _draw_neon(self, p: QPainter, rect: QRectF, radius: int,
                   color: QColor, state: int):
        cx = rect.x() + rect.width()  / 2
        cy = rect.y() + rect.height() / 2
        rg = max(rect.width(), rect.height()) * 0.75

        tint = QColor(color)
        tint.setRed(max(0, tint.red()   // 6))
        tint.setGreen(max(0, tint.green() // 6))
        tint.setBlue(max(0, tint.blue()  // 6))

        p.setBrush(QBrush(tint))
        p.drawRoundedRect(rect, radius, radius)

        bright = QColor(color); bright.setAlpha(200)
        mid    = QColor(color); mid.setAlpha(60)
        edge   = QColor(color); edge.setAlpha(0)

        rgrad = QRadialGradient(cx, cy, rg * 0.55)
        rgrad.setColorAt(0.0, bright)
        rgrad.setColorAt(0.5, mid)
        rgrad.setColorAt(1.0, edge)
        p.setBrush(QBrush(rgrad))
        p.drawRoundedRect(rect, radius, radius)

        glow_wide   = self._glow(color, 55)
        glow_bright = self._glow(color, 200)

        p.setPen(QPen(glow_wide, 3))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)

        p.setPen(QPen(glow_bright, 1))
        p.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        if state in (START_S, END_S, PATH_S):
            shine = QLinearGradient(rect.topLeft(),
                                    QRectF(rect.x(), rect.y() + rect.height() * 0.4,
                                           0, 0).topLeft())
            s0 = QColor("#ffffff"); s0.setAlpha(55)
            s1 = QColor("#ffffff"); s1.setAlpha(0)
            shine.setColorAt(0.0, s0)
            shine.setColorAt(1.0, s1)
            p.setBrush(QBrush(shine))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(rect.x() + 1, rect.y() + 1,
                                     rect.width() - 2, rect.height() * 0.45),
                              radius, radius)

        p.setPen(Qt.PenStyle.NoPen)

    def _draw_label(self, p: QPainter, pos, text: str, cs: int, color: QColor):
        r, c = pos
        font_size = max(6, cs // 3)
        p.setFont(QFont("Courier New", font_size, QFont.Weight.Bold))

        glow_pen = QPen(self._glow(color, 120), 3)
        p.setPen(glow_pen)
        p.drawText(c * cs, r * cs, cs, cs, Qt.AlignmentFlag.AlignCenter, text)

        p.setPen(QPen(QColor("#04050a")))
        p.drawText(c * cs, r * cs, cs, cs, Qt.AlignmentFlag.AlignCenter, text)

    def _cell(self, pos):
        cs = self.cell_size
        r  = pos.y() // cs
        c  = pos.x() // cs
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None

    def mousePressEvent(self, e):
        if self.running:
            return
        cell = self._cell(e.position().toPoint())
        if not cell:
            return
        r, c = cell
        if self.mode == "start":
            self._clear_state(START_S)
            self.start = (r, c)
            self.cells[r][c] = START_S
        elif self.mode == "end":
            self._clear_state(END_S)
            self.end = (r, c)
            self.cells[r][c] = END_S
        elif self.mode == "wall":
            if self.cells[r][c] not in (START_S, END_S):
                self.draw_mode = self.cells[r][c] != WALL_S
                self.cells[r][c] = WALL_S if self.draw_mode else EMPTY_S
        self._last_cell = cell
        self.update()

    def mouseMoveEvent(self, e):
        if self.running or self.mode != "wall" or self.draw_mode is None:
            return
        cell = self._cell(e.position().toPoint())
        if not cell:
            return

        if self._last_cell and self._last_cell != cell:
            for (ir, ic) in self._bresenham(self._last_cell, cell):
                if self.cells[ir][ic] not in (START_S, END_S):
                    self.cells[ir][ic] = WALL_S if self.draw_mode else EMPTY_S
        else:
            r, c = cell
            if self.cells[r][c] not in (START_S, END_S):
                self.cells[r][c] = WALL_S if self.draw_mode else EMPTY_S

        self._last_cell = cell
        self.update()

    def mouseReleaseEvent(self, _):
        self.draw_mode  = None
        self._last_cell = None

    def _bresenham(self, start, end):
        r0, c0 = start
        r1, c1 = end

        dc = abs(c1 - c0);  sc = 1 if c0 < c1 else -1
        dr = -abs(r1 - r0); sr = 1 if r0 < r1 else -1
        err = dc + dr

        while True:
            yield (r0, c0)
            if r0 == r1 and c0 == c1:
                break
            e2 = 2 * err
            if e2 >= dr:
                if c0 == c1:
                    break
                err += dr
                c0  += sc
            if e2 <= dc:
                if r0 == r1:
                    break
                err += dc
                r0  += sr

    def _clear_state(self, state):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c] == state:
                    self.cells[r][c] = EMPTY_S

    def _clear_search(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c] in (VISITED_S, FRONTIER_S, PATH_S):
                    self.cells[r][c] = EMPTY_S

    def clear_all(self):
        self.timer.stop()
        self.running = False
        self.cells = [[EMPTY_S] * self.cols for _ in range(self.rows)]
        self.start = None
        self.end   = None
        self.update()
        self.status_changed.emit("Grid cleared.")

    def clear_path(self):
        self.timer.stop()
        self.running = False
        self._clear_search()
        self.update()
        self.status_changed.emit("Path cleared.")

    def run(self):
        if not self.start or not self.end:
            self.status_changed.emit("⚠  Place start (S) and end (E) first.")
            return
        self._clear_search()
        self.cells[self.start[0]][self.start[1]] = START_S
        self.cells[self.end[0]][self.end[1]]     = END_S

        algo = self.algorithm
        if algo == "bfs":
            visited_order, came_from = self._bfs()
        elif algo == "dfs":
            visited_order, came_from = self._dfs()
        else:
            visited_order, came_from = self._astar()

        if came_from is None:
            self.status_changed.emit("✕  No path found.")
            return

        path = self._reconstruct(came_from)
        self.anim_steps = [("v", c) for c in visited_order] + [("p", c) for c in path]
        self.anim_index = 0
        self.running    = True
        self.status_changed.emit(f"Running {algo.upper()}…")
        self.timer.start(14)

    def _step(self):
        if self.anim_index >= len(self.anim_steps):
            self.timer.stop()
            self.running = False
            path_len = sum(1 for t, _ in self.anim_steps if t == "p")
            vis_len  = sum(1 for t, _ in self.anim_steps if t == "v")
            self.status_changed.emit(
                f"✓  Path: {path_len} cells   Visited: {vis_len} cells"
            )
            return
        kind, (r, c) = self.anim_steps[self.anim_index]
        if (r, c) not in (self.start, self.end):
            self.cells[r][c] = PATH_S if kind == "p" else VISITED_S
        self.anim_index += 1
        self.update()

    def _neighbors(self, r, c):
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.cells[nr][nc] != WALL_S:
                    yield nr, nc

    def _bfs(self):
        q = deque([self.start])
        came_from = {self.start: None}
        order = []
        while q:
            cur = q.popleft()
            if cur == self.end:
                return order, came_from
            for nb in self._neighbors(*cur):
                if nb not in came_from:
                    came_from[nb] = cur
                    order.append(nb)
                    q.append(nb)
        return order, None

    def _dfs(self):
        stack = [self.start]
        came_from = {self.start: None}
        order = []
        while stack:
            cur = stack.pop()
            if cur == self.end:
                return order, came_from
            for nb in self._neighbors(*cur):
                if nb not in came_from:
                    came_from[nb] = cur
                    order.append(nb)
                    stack.append(nb)
        return order, None

    def _astar(self):
        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set  = [(0, self.start)]
        came_from = {self.start: None}
        g         = {self.start: 0}
        order     = []
        while open_set:
            _, cur = heapq.heappop(open_set)
            if cur == self.end:
                return order, came_from
            for nb in self._neighbors(*cur):
                ng = g[cur] + 1
                if nb not in g or ng < g[nb]:
                    g[nb] = ng
                    heapq.heappush(open_set, (ng + h(nb, self.end), nb))
                    came_from[nb] = cur
                    order.append(nb)
        return order, None

    def _reconstruct(self, came_from):
        path, node = [], self.end
        while node and node != self.start:
            path.append(node)
            node = came_from.get(node)
        path.reverse()
        return path