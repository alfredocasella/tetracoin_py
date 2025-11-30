import pygame

# Screen settings (Portrait Mode - Mobile First)
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
TITLE = "TetraCoin"
FPS = 60

# Layout Settings
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
# Web Prototype Color Palette
BG_COLOR = (242, 247, 255)  # #F2F7FF
GRID_CONTAINER_BG = (245, 249, 255) # #F5F9FF
GRID_CONTAINER_BORDER = (208, 215, 226) # #D0D7E2

GRID_CELL_EMPTY_BG = (234, 241, 255) # #EAF1FF
GRID_CELL_EMPTY_BORDER = (208, 215, 226) # #D0D7E2

GRID_CELL_WALL_BG = (138, 143, 160) # #8A8FA0
GRID_CELL_WALL_BORDER = (122, 129, 144) # #7A8190

GRID_LINE_COLOR = (208, 215, 226) # Re-added for compatibility (matches border)

TEXT_COLOR = (26, 33, 48) # #1A2130

# UI Colors
COLOR_PRIMARY_TEAL = (0, 194, 168) # #00C2A8
COLOR_WHITE = (255, 255, 255)
COLOR_ERROR_RED = (255, 90, 90)
COLOR_WARNING_ORANGE = (255, 159, 67)
COLOR_SUCCESS_GREEN = (51, 204, 122) # Using Green from palette

# Block Colors (Fill and Border)
BLOCK_COLORS = {
    "YELLOW": {"fill": (255, 201, 77), "border": (217, 152, 31)}, # #FFC94D, #D9981F
    "BLUE":   {"fill": (79, 139, 255), "border": (42, 87, 191)},  # #4F8BFF, #2A57BF
    "RED":    {"fill": (255, 90, 90),  "border": (194, 48, 48)},  # #FF5A5A, #C23030
    "GREEN":  {"fill": (51, 204, 122), "border": (34, 153, 87)},  # #33CC7A, #229957
    "PURPLE": {"fill": (184, 112, 255),"border": (124, 58, 194)}, # #B870FF, #7C3AC2
}

# Coin Colors (Fill and Border)
COIN_COLORS = {
    "YELLOW": {"fill": (255, 214, 107), "border": (217, 168, 66)}, # #FFD66B, #D9A842
    "BLUE":   {"fill": (107, 160, 255), "border": (62, 107, 217)}, # #6BA0FF, #3E6BD9
    "RED":    {"fill": (255, 122, 122), "border": (217, 71, 71)},  # #FF7A7A, #D94747
    "GREEN":  {"fill": (77, 222, 138),  "border": (46, 170, 96)},  # #4DDE8A, #2EAA60
    "PURPLE": {"fill": (200, 138, 255), "border": (138, 75, 217)}, # #C88AFF, #8A4BD9
}

# Map string keys to these dicts for compatibility
COLORS = {k: v["fill"] for k, v in BLOCK_COLORS.items()}
