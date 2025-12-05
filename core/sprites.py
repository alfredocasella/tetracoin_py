import pygame
import os
from core.settings import *

import math

# Tetris shape definitions (relative coordinates from origin)
SHAPES = {
    'I2': [(0, 0), (1, 0)],           # Horizontal 2-block
    'I3': [(0, 0), (1, 0), (2, 0)],   # Horizontal 3-block
    'I4': [(0, 0), (1, 0), (2, 0), (3, 0)],  # Horizontal 4-block
    'L4': [(0, 0), (0, 1), (0, 2), (1, 2)],  # L-shape
    'J4': [(1, 0), (1, 1), (1, 2), (0, 2)],  # J-shape (mirrored L)
    'O4': [(0, 0), (1, 0), (0, 1), (1, 1)],  # Square
    'T4': [(0, 0), (1, 0), (2, 0), (1, 1)],  # T-shape
    'S4': [(1, 0), (2, 0), (0, 1), (1, 1)],  # S-shape
    'Z4': [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z-shape
    'T': [(0, 0), (1, 0), (2, 0), (1, 1)],   # Alias for T4
    'L': [(0, 0), (0, 1), (0, 2), (1, 2)],   # Alias for L4
    'I': [(0, 0), (1, 0)],                    # Alias for I2
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],   # Alias for O4
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],   # Alias for S4
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)],   # Alias for Z4
}

from src.tetracoin.utils import deprecated

@deprecated("Replaced by spec.Entity types (PIGGYBANK, OBSTACLE)")
class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, block_data, groups, grid_offsets=None, tile_size=TILE_SIZE):
        super().__init__(groups)
        self.block_data = block_data
        self.grid_x, self.grid_y = block_data['start_pos']
        self.counter = block_data['count']
        self.shape_name = block_data.get('shape', 'I2')
        self.shape_cells = SHAPES.get(self.shape_name, [(0, 0)])  # Get shape or default to single cell
        self.tile_size = tile_size
        
        # Use provided offsets or fallback to settings
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        # Visual properties
        self.selected = False
        self.color = COLORS.get(block_data['color'], (200, 200, 200))
        
        # Calculate bounding box for the entire shape
        max_x = max(cell[0] for cell in self.shape_cells)
        max_y = max(cell[1] for cell in self.shape_cells)
        # Calculate bounding box for the entire shape
        max_x = max(cell[0] for cell in self.shape_cells)
        max_y = max(cell[1] for cell in self.shape_cells)
        self.width = (max_x + 1) * self.tile_size
        self.height = (max_y + 1) * self.tile_size
        
        # Load sprite or create primitive
        self.sprite_image = None
        sprite_path = os.path.join("assets", "images", f"block_{block_data['color']}.png")
        if os.path.exists(sprite_path):
            try:
                self.sprite_image = pygame.image.load(sprite_path)
                self.sprite_image = pygame.transform.scale(self.sprite_image, (self.tile_size, self.tile_size))
            except:
                pass
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # CRITICAL: Set position BEFORE update_appearance
        # CRITICAL: Set position BEFORE update_appearance
        self.target_x = self.offset_x + self.grid_x * self.tile_size
        self.target_y = self.offset_y + self.grid_y * self.tile_size
        self.rect.x = self.target_x
        self.rect.y = self.target_y
        
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Now update appearance (draws on the surface)
        self.update_appearance()

    def get_occupied_cells(self):
        """Return list of all grid cells occupied by this block"""
        return [(self.grid_x + dx, self.grid_y + dy) for dx, dy in self.shape_cells]

    def update_appearance(self):
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        # Get colors
        color_key = self.block_data['color']
        colors = BLOCK_COLORS.get(color_key, BLOCK_COLORS['YELLOW'])
    def update_appearance(self):
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        # Get colors
        color_key = self.block_data['color']
        colors = BLOCK_COLORS.get(color_key, BLOCK_COLORS['YELLOW'])
        
        # Mockup Style: "Hollow Tray"
        # 1. Draw the "Floor" (Inner Shadow) - Darker color
        # 2. Draw the "Walls" (Outer Border) - Main color, thick
        
        wall_color = colors['main']
        floor_color = colors['dark']
        
        wall_thickness = 8 # Thick walls
        
        # We need to draw the unified shape.
        # Since we don't have a complex polygon merger, we'll draw per-cell
        # but carefully to make it look unified.
        
        # 1. Draw Floor (The dark inner part)
        # It should be inset by wall_thickness
        
        # Strategy: Draw full cells in Wall Color, then draw smaller cells in Floor Color on top
        
        # Pass 1: Draw Walls (Base)
        for dx, dy in self.shape_cells:
            cell_x = dx * self.tile_size
            cell_y = dy * self.tile_size
            
            # Draw full cell in wall color
            # We add a small overlap to merge adjacent cells visually
            rect = pygame.Rect(cell_x, cell_y, self.tile_size, self.tile_size)
            pygame.draw.rect(self.image, wall_color, rect)
            
        # Pass 2: Draw Floor (Inner Dark Part)
        # We only draw the floor if the side is NOT connected to another cell
        # Actually, for a hollow tray look, the floor is continuous inside.
        # So we draw the floor in the center of each cell, and connect them if neighbors exist.
        
        for dx, dy in self.shape_cells:
            cell_x = dx * self.tile_size
            cell_y = dy * self.tile_size
            
            # Inner rect for this cell
            inner_rect = pygame.Rect(
                cell_x + wall_thickness, 
                cell_y + wall_thickness, 
                self.tile_size - 2 * wall_thickness, 
                self.tile_size - 2 * wall_thickness
            )
            pygame.draw.rect(self.image, floor_color, inner_rect)
            
            # Connect to neighbors (fill the gap in the wall)
            neighbors = {
                'top': (dx, dy - 1) in self.shape_cells,
                'bottom': (dx, dy + 1) in self.shape_cells,
                'left': (dx - 1, dy) in self.shape_cells,
                'right': (dx + 1, dy) in self.shape_cells
            }
            
            if neighbors['top']:
                # Fill gap upwards
                gap_rect = pygame.Rect(inner_rect.left, cell_y, inner_rect.width, wall_thickness)
                pygame.draw.rect(self.image, floor_color, gap_rect)
                
            if neighbors['bottom']:
                # Fill gap downwards
                gap_rect = pygame.Rect(inner_rect.left, inner_rect.bottom, inner_rect.width, wall_thickness)
                pygame.draw.rect(self.image, floor_color, gap_rect)
                
            if neighbors['left']:
                # Fill gap left
                gap_rect = pygame.Rect(cell_x, inner_rect.top, wall_thickness, inner_rect.height)
                pygame.draw.rect(self.image, floor_color, gap_rect)
                
            if neighbors['right']:
                # Fill gap right
                gap_rect = pygame.Rect(inner_rect.right, inner_rect.top, wall_thickness, inner_rect.height)
                pygame.draw.rect(self.image, floor_color, gap_rect)

        # Pass 3: Highlights/Bevels on Walls (Optional, for 3D effect)
        # Top/Left edges of walls could be lighter
        highlight_color = (255, 255, 255, 100)
        for dx, dy in self.shape_cells:
            cell_x = dx * self.tile_size
            cell_y = dy * self.tile_size
            
            # If no top neighbor, draw highlight on top wall
            if (dx, dy - 1) not in self.shape_cells:
                pygame.draw.rect(self.image, highlight_color, (cell_x, cell_y, self.tile_size, 3))
                
        # Pass 4: Number Badge (White square in corner)
        # Find the "last" cell or a specific corner (e.g., bottom-right most)
        # For simplicity, let's pick the cell with max x + max y
        target_cell = max(self.shape_cells, key=lambda p: p[0] + p[1])
        
        if self.counter > 0:
            badge_size = 20
            bx = target_cell[0] * self.tile_size + self.tile_size - badge_size - 4
            by = target_cell[1] * self.tile_size + self.tile_size - badge_size - 4
            
            # White rounded rect
            badge_rect = pygame.Rect(bx, by, badge_size, badge_size)
            pygame.draw.rect(self.image, (255, 255, 255), badge_rect, border_radius=5)
            
            # Number
            font = pygame.font.Font(None, 20)
            text = font.render(str(self.counter), True, (0, 0, 0))
            text_rect = text.get_rect(center=badge_rect.center)
            self.image.blit(text, text_rect)

    def _draw_3d_cell(self, x, y):
        # Deprecated, replaced by update_appearance container logic
        pass

    def move(self, dx, dy):
        self.grid_x += dx
        self.grid_y += dy
        
    def select(self):
        self.selected = True
        self.update_appearance()
        
    def deselect(self):
        self.selected = False
        self.update_appearance()
        
    def update(self):
        # Smooth movement to target position
        # If dragging, position is set by mouse
        if not self.dragging:
            self.target_x = self.offset_x + self.grid_x * self.tile_size
            self.target_y = self.offset_y + self.grid_y * self.tile_size
            
            # Simple lerp or direct set
            self.rect.x += (self.target_x - self.rect.x) * 0.5
            self.rect.y += (self.target_y - self.rect.y) * 0.5
            
            # Snap if close
            if abs(self.rect.x - self.target_x) < 1 and abs(self.rect.y - self.target_y) < 1:
                self.rect.x = self.target_x
                self.rect.y = self.target_y

class CoinSprite(pygame.sprite.Sprite):
    # Class-level cache for base sprite
    _base_sprite = None
    
    def __init__(self, coin_data, groups, grid_offsets=None, tile_size=TILE_SIZE):
        super().__init__(groups)
        self.coin_data = coin_data
        self.grid_x, self.grid_y = coin_data['pos']
        
        # Use provided offsets or fallback to settings
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        self.base_size = tile_size
        # Increase height to accommodate the stack
        self.image = pygame.Surface((self.base_size, self.base_size + 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # Set initial position
        # Adjust Y to align the bottom of the stack with the cell bottom
        # The stack grows upwards, so the "base" of the stack should be at the cell's bottom area
        self.rect.x = self.offset_x + self.grid_x * self.base_size
        # Shift up slightly to center the visual weight or align bottom
        # We want the bottom of the coin stack (at bottom_y in _generate) to align with cell bottom
        # In _generate, bottom_y = height - 10.
        # So visual bottom is at rect.y + height - 10.
        # We want visual bottom at offset_y + (grid_y + 1) * tile_size - padding
        # Let's just center it horizontally and align bottom with some padding
        
        self.rect.y = self.offset_y + self.grid_y * self.base_size - 15 
        
        # Animation state
        self.original_y = self.rect.y
        self.pulse_time = 0
        
        # Generate the coin stack image
        self._generate_coin_image()
        
    def _generate_coin_image(self):
        """Generate a stack of 3 coins using vector drawing"""
        self.image.fill((0, 0, 0, 0))
        
        color_key = self.coin_data['color']
        colors = COIN_COLORS.get(color_key, COIN_COLORS['YELLOW'])
        
        fill_color = colors['fill']
        # Use the border color defined in settings as the "side" (darker) color
        side_color = colors['border'] 
        # Create a darker outline color
        outline_color = (
            max(0, side_color[0] - 50),
            max(0, side_color[1] - 50),
            max(0, side_color[2] - 50)
        )
        
        # Coin dimensions
        coin_w = self.base_size - 10 # Slight padding
        coin_h = 12 # Thickness of the cylinder
        oval_h = 14 # Height of the top/bottom ellipse (perspective)
        
        center_x = self.image.get_width() // 2
        bottom_y = self.image.get_height() - 10
        
        # Draw stack of 3 coins (bottom to top)
        num_coins = 3
        stack_overlap = 8 # How much they overlap vertically
        
        for i in range(num_coins):
            # Calculate Y position for this coin
            # i=0 is bottom, i=2 is top
            y = bottom_y - (i * stack_overlap) - coin_h
            
            # Rects for drawing
            # Top face bounds
            top_rect = pygame.Rect(center_x - coin_w//2, y, coin_w, oval_h)
            # Bottom face bounds (for the cylinder bottom curve)
            bottom_rect = pygame.Rect(center_x - coin_w//2, y + coin_h, coin_w, oval_h)
            
            # 1. Draw Cylinder Body (Side)
            # Rectangle part
            body_rect = pygame.Rect(center_x - coin_w//2, y + oval_h//2, coin_w, coin_h)
            pygame.draw.rect(self.image, side_color, body_rect)
            
            # Bottom curve (Ellipse)
            pygame.draw.ellipse(self.image, side_color, bottom_rect)
            
            # Side Outline (Vertical lines)
            pygame.draw.line(self.image, outline_color, body_rect.topleft, body_rect.bottomleft, 2)
            pygame.draw.line(self.image, outline_color, body_rect.topright, body_rect.bottomright, 2)
            
            # Bottom Curve Outline (Half ellipse)
            pygame.draw.arc(self.image, outline_color, bottom_rect, math.pi, 0, 2)
            
            # 2. Draw Top Face
            pygame.draw.ellipse(self.image, fill_color, top_rect)
            pygame.draw.ellipse(self.image, outline_color, top_rect, 2)
            
            # Highlight on top face (small white ellipse or arc)
            highlight_rect = top_rect.inflate(-10, -6)
            highlight_rect.y += 2
            # pygame.draw.ellipse(self.image, (255, 255, 255, 100), highlight_rect)
            
    def update(self):
        # Simple floating animation?
        pass

    def trigger_sparkle(self):
        pass
