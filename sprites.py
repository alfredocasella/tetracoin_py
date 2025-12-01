import pygame
import os
from settings import *

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

class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, block_data, groups, grid_offsets=None):
        super().__init__(groups)
        self.block_data = block_data
        self.grid_x, self.grid_y = block_data['start_pos']
        self.counter = block_data['count']
        self.shape_name = block_data.get('shape', 'I2')
        self.shape_cells = SHAPES.get(self.shape_name, [(0, 0)])  # Get shape or default to single cell
        
        # Use provided offsets or fallback to settings
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        # Visual properties
        self.selected = False
        self.color = COLORS.get(block_data['color'], (200, 200, 200))
        
        # Calculate bounding box for the entire shape
        max_x = max(cell[0] for cell in self.shape_cells)
        max_y = max(cell[1] for cell in self.shape_cells)
        self.width = (max_x + 1) * TILE_SIZE
        self.height = (max_y + 1) * TILE_SIZE
        
        # Load sprite or create primitive
        self.sprite_image = None
        sprite_path = os.path.join("assets", "images", f"block_{block_data['color']}.png")
        if os.path.exists(sprite_path):
            try:
                self.sprite_image = pygame.image.load(sprite_path)
                self.sprite_image = pygame.transform.scale(self.sprite_image, (TILE_SIZE, TILE_SIZE))
            except:
                pass
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # CRITICAL: Set position BEFORE update_appearance
        self.target_x = self.offset_x + self.grid_x * TILE_SIZE
        self.target_y = self.offset_y + self.grid_y * TILE_SIZE
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
            cell_x = dx * TILE_SIZE
            cell_y = dy * TILE_SIZE
            
            # Draw full cell in wall color
            # We add a small overlap to merge adjacent cells visually
            rect = pygame.Rect(cell_x, cell_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.image, wall_color, rect)
            
        # Pass 2: Draw Floor (Inner Dark Part)
        # We only draw the floor if the side is NOT connected to another cell
        # Actually, for a hollow tray look, the floor is continuous inside.
        # So we draw the floor in the center of each cell, and connect them if neighbors exist.
        
        for dx, dy in self.shape_cells:
            cell_x = dx * TILE_SIZE
            cell_y = dy * TILE_SIZE
            
            # Inner rect for this cell
            inner_rect = pygame.Rect(
                cell_x + wall_thickness, 
                cell_y + wall_thickness, 
                TILE_SIZE - 2 * wall_thickness, 
                TILE_SIZE - 2 * wall_thickness
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
            cell_x = dx * TILE_SIZE
            cell_y = dy * TILE_SIZE
            
            # If no top neighbor, draw highlight on top wall
            if (dx, dy - 1) not in self.shape_cells:
                pygame.draw.rect(self.image, highlight_color, (cell_x, cell_y, TILE_SIZE, 3))
                
        # Pass 4: Number Badge (White square in corner)
        # Find the "last" cell or a specific corner (e.g., bottom-right most)
        # For simplicity, let's pick the cell with max x + max y
        target_cell = max(self.shape_cells, key=lambda p: p[0] + p[1])
        
        if self.counter > 0:
            badge_size = 20
            bx = target_cell[0] * TILE_SIZE + TILE_SIZE - badge_size - 4
            by = target_cell[1] * TILE_SIZE + TILE_SIZE - badge_size - 4
            
            # White rounded rect
            badge_rect = pygame.Rect(bx, by, badge_size, badge_size)
            pygame.draw.rect(self.image, (255, 255, 255), badge_rect, border_radius=5)
            
            # Number
            font = pygame.font.SysFont("Arial", 14, bold=True)
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
            self.target_x = self.offset_x + self.grid_x * TILE_SIZE
            self.target_y = self.offset_y + self.grid_y * TILE_SIZE
            
            # Simple lerp or direct set
            self.rect.x += (self.target_x - self.rect.x) * 0.5
            self.rect.y += (self.target_y - self.rect.y) * 0.5
            
            # Snap if close
            if abs(self.rect.x - self.target_x) < 1 and abs(self.rect.y - self.target_y) < 1:
                self.rect.x = self.target_x
                self.rect.y = self.target_y

class CoinSprite(pygame.sprite.Sprite):
    def __init__(self, coin_data, groups, grid_offsets=None):
        super().__init__(groups)
        self.coin_data = coin_data
        self.grid_x, self.grid_y = coin_data['pos']
        self.color = COLORS.get(coin_data['color'], (255, 215, 0))
        
        # Use provided offsets or fallback to settings
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        # Debug print to verify offsets
        # print(f"Coin spawned at {self.grid_x},{self.grid_y} with offsets {self.offset_x},{self.offset_y}")
        
        self.base_size = TILE_SIZE
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.base_image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # Set initial position
        self.rect.x = self.offset_x + self.grid_x * TILE_SIZE
        self.rect.y = self.offset_y + self.grid_y * TILE_SIZE
        
        # Animation state
        self.original_y = self.rect.y
        self.pulse_time = 0
        
        self._create_3d_coin()
        self.update()
        
    def _create_3d_coin(self):
        """Create a Coin matching Web Prototype style"""
        # Clear surface
        self.base_image.fill((0,0,0,0))
        
        center = self.base_size // 2
        # Reduce radius to fit inside cell with padding
        # Cell is TILE_SIZE - 4. Coin should be smaller.
        # Let's make it TILE_SIZE - 12 (6px padding on each side)
        radius = (self.base_size - 12) // 2
        
        # Get colors
        color_key = self.coin_data['color']
        colors = COIN_COLORS.get(color_key, COIN_COLORS['YELLOW'])
        fill_color = colors['fill']
        border_color = colors['border']
        
        # Shadow
        shadow_rect = pygame.Rect(center - radius, center - radius + 4, radius * 2, radius * 2)
        pygame.draw.circle(self.base_image, (0, 0, 0, 40), (center, center + 4), radius)
        
        # Main Body (Circle)
        pygame.draw.circle(self.base_image, fill_color, (center, center), radius)
        
        # Border
        pygame.draw.circle(self.base_image, border_color, (center, center), radius, 3)
        
        # Radial Gradient Simulation (Light top-left, Dark bottom-right)
        # Highlight
        pygame.draw.circle(self.base_image, (255, 255, 255), (center - radius//3, center - radius//3), radius//3)
        
        # Sparkle Icon (Cross)
        sparkle_color = border_color
        cx, cy = center, center
        size = radius * 0.5
        
        # Draw star
        points = [
            (cx, cy - size), (cx + size * 0.2, cy - size * 0.2),
            (cx + size, cy), (cx + size * 0.2, cy + size * 0.2),
            (cx, cy + size), (cx - size * 0.2, cy + size * 0.2),
            (cx - size, cy), (cx - size * 0.2, cy - size * 0.2)
        ]
        pygame.draw.polygon(self.base_image, sparkle_color, points)
        
    def update(self):
        # Static position (No bouncing)
        # Just handle sparkle effect
        
        # Randomly trigger sparkle
        import random
        if random.random() < 0.02: # 2% chance per frame
            self.trigger_sparkle()
            
        # Draw sparkle if active
        if hasattr(self, 'sparkle_timer') and self.sparkle_timer > 0:
            self.sparkle_timer -= 1
            
            # Re-draw base coin first to clear previous sparkle frame
            self.image = self.base_image.copy()
            
            # Draw sparkle
            center = self.base_size // 2
            radius = self.base_size // 3
            
            # Sparkle position (top right usually looks good)
            sx = center + radius // 2
            sy = center - radius // 2
            
            # Pulsing size
            size = 4 + (10 - abs(10 - self.sparkle_timer)) // 2
            
            # Draw star/cross shape
            white = (255, 255, 255)
            pygame.draw.line(self.image, white, (sx - size, sy), (sx + size, sy), 2)
            pygame.draw.line(self.image, white, (sx, sy - size), (sx, sy + size), 2)
        else:
            # Ensure image is clean
            if self.image != self.base_image:
                self.image = self.base_image.copy()

    def trigger_sparkle(self):
        self.sparkle_timer = 20 # Frames to show sparkle_offset
