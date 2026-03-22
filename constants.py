from PyQt6.QtGui import QColor

# ── Palette ── void black + cyan/magenta neon ─────────────────────────────────
BG          = QColor("#04050a")   # void black, slightly blue-tinted
BG_PANEL    = QColor("#070810")   # panel — deepest dark
BG_CARD     = QColor("#0c0e1a")   # card bg
BORDER      = QColor("#151828")   # barely-visible cool border
BORDER_LIT  = QColor("#1e2540")   # lit border

GRID_LINE   = QColor("#0a0c16")   # near-invisible cool-dark grid gap
EMPTY       = QColor("#080a14")   # cell void

# Walls: dark gunmetal with blue tint
WALL        = QColor("#1a1f2e")

# Nodes
START       = QColor("#00ffe5")   # electric cyan
END         = QColor("#ff2d78")   # hot magenta/pink

# Search states — pure neon
VISITED     = QColor("#59acff")   # deep navy pulse
FRONTIER    = QColor("#0055ff")   # electric indigo-blue
PATH        = QColor("#ffe600")   # pure neon yellow

# Panel accents
ACCENT      = QColor("#00ffe5")   # cyan
ACCENT2     = QColor("#ff2d78")   # magenta
SUCCESS     = QColor("#00ffe5")
DANGER      = QColor("#ff2d78")

TEXT        = QColor("#c8d8f0")   # cool light blue-white
TEXT_DIM    = QColor("#3a4a6a")   # muted blue-grey
TEXT_BRIGHT = QColor("#e8f4ff")   # near-white cool

# Grid dimensions
ROWS = 25
COLS = 40

# Cell States
EMPTY_S    = 0
WALL_S     = 1
START_S    = 2
END_S      = 3
VISITED_S  = 4
FRONTIER_S = 5
PATH_S     = 6