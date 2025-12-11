import pygame

# Screen settings (Portrait Mode - Mobile First)
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
TITLE = "TetraCoin"
FPS = 60

# Layout Settings
SAFE_AREA_TOP = 40    # Space for status bar/notch
TOP_HUD_HEIGHT = 90       # Further reduced from 100
BOTTOM_BAR_HEIGHT = 110   # Reduced from 120
OBJECTIVE_PANEL_HEIGHT = 160  # Increased from 140 for better visibility
GRID_AREA_HEIGHT = SCREEN_HEIGHT - TOP_HUD_HEIGHT - BOTTOM_BAR_HEIGHT - OBJECTIVE_PANEL_HEIGHT
# Grid offsets will be calculated dynamically in Game class, but providing defaults
GRID_OFFSET_X = 30        # Reduced from 40
GRID_OFFSET_Y = TOP_HUD_HEIGHT + 15  # Reduced margin

# Grid settings
TILE_SIZE = 50  # Reduced from 52 to 50 for even more compact fit (7*50=350px)

# Modern Cartoon Color Palette
# Drop Away Style Colors
BG_COLOR = (200, 230, 250)  # Light blue background like Drop Away

# Header
HEADER_BG = (106, 27, 154) # Purple #6A1B9A
HEADER_BUTTON_YELLOW = (255, 193, 7) # Amber #FFC107
HEADER_BUTTON_BORDER = (255, 111, 0) # Darker Orange #FF6F00
HEADER_TIMER_BG = (62, 39, 35) # Dark Brown #3E2723

# Grid Tray
TRAY_BG = (129, 212, 250) # Light Blue Tray #81D4FA
TRAY_BORDER = (41, 182, 246) # Darker Blue Border #29B6F6
TRAY_SHADOW = (2, 119, 189) # Deep Blue Shadow #0277BD

# Grid Cells
GRID_CELL_BG = (224, 224, 224) # Light Gray #E0E0E0
GRID_LINE_COLOR = (189, 189, 189) # Gray #BDBDBD

# Text
TEXT_COLOR = (255, 255, 255) # White text for header
TEXT_COLOR_DARK = (60, 60, 60) # Dark text for other areas

# UI Colors
COLOR_PRIMARY_TEAL = (0, 194, 168) # Keep for legacy/accents
COLOR_WHITE = (255, 255, 255)

# Block Colors (Vibrant, "Tray" look)
# Format: {Fill (Walls), Dark (Inner Shadow/Floor)}
BLOCK_COLORS = {
    "YELLOW": {"main": (255, 213, 79), "dark": (196, 144, 0)},   # Amber
    "BLUE":   {"main": (33, 150, 243), "dark": (13, 71, 161)},   # Blue
    "RED":    {"main": (244, 67, 54),  "dark": (183, 28, 28)},   # Red
    "GREEN":  {"main": (76, 175, 80),  "dark": (27, 94, 32)},    # Green
    "PURPLE": {"main": (156, 39, 176), "dark": (74, 20, 140)},   # Purple
    "ORANGE": {"main": (255, 152, 0),  "dark": (230, 81, 0)},    # Orange
    "PINK":   {"main": (233, 30, 99),  "dark": (136, 14, 79)},   # Pink
}

# Coin Colors
COIN_COLORS = {
    "YELLOW": {"fill": (255, 215, 0), "border": (184, 134, 11)},
    "BLUE":   {"fill": (64, 196, 255), "border": (0, 145, 234)},
    "RED":    {"fill": (255, 82, 82), "border": (211, 47, 47)},
    "GREEN":  {"fill": (105, 240, 174), "border": (0, 200, 83)},
    "PURPLE": {"fill": (224, 64, 251), "border": (170, 0, 255)},
}

# Map string keys to these dicts for compatibility
COLORS = {k: v["main"] for k, v in BLOCK_COLORS.items()}
