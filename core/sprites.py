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
        # ========== DROP AWAY STYLE 3D BLOCKS ==========
        # Enhanced rendering with gradients, shadows, and depth
        
        color_key = self.block_data.get('color', 'YELLOW')
        colors = BLOCK_COLORS.get(color_key, BLOCK_COLORS['YELLOW'])
        
        wall_color = colors['main']
        floor_color = colors['dark']
        wall_thickness = 8
        
        # Pass 1: Draw shadow under block for 3D depth
        shadow_offset = 4
        for dx, dy in self.shape_cells:
            cell_x = dx * self.tile_size
            cell_y = dy * self.tile_size
            shadow_rect = pygame.Rect(
                cell_x + shadow_offset,
                cell_y + shadow_offset,
                self.tile_size,
                self.tile_size
            )
            pygame.draw.rect(self.image, (0, 0, 0, 60), shadow_rect, border_radius=8)
        
        # Pass 2: Draw Walls (Base) with gradient effect
        for dx, dy in self.shape_cells:
            cell_x = dx * self.tile_size
            cell_y = dy * self.tile_size
            
            # Draw full cell in wall color
            rect = pygame.Rect(cell_x, cell_y, self.tile_size, self.tile_size)
            pygame.draw.rect(self.image, wall_color, rect, border_radius=8)
            
            # Add highlight on top for 3D effect (lighter color)
            highlight_color = tuple(min(255, c + 40) for c in wall_color)
            highlight_rect = pygame.Rect(cell_x, cell_y, self.tile_size, self.tile_size // 3)
            pygame.draw.rect(self.image, highlight_color, highlight_rect, border_radius=8)
            
        # Pass 3: Draw Floor (Inner Dark Part)
        for dx, dy in self.shape_cells:
            cell_x = dx * self.tile_size
            cell_y = dy * self.tile_size
            
            inner_rect = pygame.Rect(
                cell_x + wall_thickness,
                cell_y + wall_thickness,
                self.tile_size - 2 * wall_thickness,
                self.tile_size - 2 * wall_thickness
            )
            pygame.draw.rect(self.image, floor_color, inner_rect, border_radius=4)
            
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
        
        
        # ========== DROP AWAY STYLE: COUNTER BADGE ==========
        # Display counter prominently on the block
        if self.counter > 0:
            # Larger badge for better visibility
            badge_size = int(self.tile_size * 0.5)  # 50% of tile size
            bx = target_cell[0] * self.tile_size + self.tile_size - badge_size - 4
            by = target_cell[1] * self.tile_size + self.tile_size - badge_size - 4
            
            # White rounded rect with shadow
            shadow_rect = pygame.Rect(bx + 2, by + 2, badge_size, badge_size)
            pygame.draw.rect(self.image, (0, 0, 0, 100), shadow_rect, border_radius=8)
            
            badge_rect = pygame.Rect(bx, by, badge_size, badge_size)
            pygame.draw.rect(self.image, (255, 255, 255), badge_rect, border_radius=8)
            
            # Number - larger and bolder
            font_size = int(badge_size * 0.7)
            font = pygame.font.Font(None, font_size)
            text = font.render(str(self.counter), True, (0, 0, 0))
            text_rect = text.get_rect(center=badge_rect.center)
            self.image.blit(text, text_rect)
        # ========== END COUNTER BADGE ==========

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
        # FIX: Make surface exactly tile_size to align with grid
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # FIX: Position exactly on grid cell (no offset)
        self.rect.x = self.offset_x + self.grid_x * self.base_size
        self.rect.y = self.offset_y + self.grid_y * self.base_size
        
        # Animation state
        self.original_y = self.rect.y
        self.pulse_time = 0
        
        # Generate the coin stack image
        self._generate_coin_image()
        
    def _generate_coin_image(self):
        """Generate realistic gold coin stack with ridged edges (like reference image)"""
        self.image.fill((0, 0, 0, 0))
        
        color_key = self.coin_data['color']
        colors = COIN_COLORS.get(color_key, COIN_COLORS['YELLOW'])
        
        # Gold coin colors
        fill_color = colors['fill']
        border_color = colors['border']
        
        # Stack of 3-4 coins
        num_coins = 3
        coin_diameter = int(self.base_size * 0.7)
        coin_thickness = 6  # Thinner coins
        
        center_x = self.base_size // 2
        center_y = self.base_size // 2
        
        # Ellipse for isometric view
        ellipse_width = coin_diameter
        ellipse_height = int(coin_diameter * 0.3)
        
        # Random offsets for realistic stacking
        import random
        random.seed(self.grid_x * 100 + self.grid_y)
        
        # Calculate positions with slight tilt/cascade
        total_height = num_coins * coin_thickness + (num_coins - 1) * 2
        start_y = center_y - total_height // 2
        
        # Draw coins from bottom to top
        for i in range(num_coins):
            # Position with slight offset for cascade effect
            offset_x = random.randint(-4, 4) if i > 0 else 0
            offset_y = i * (coin_thickness + 2)
            
            coin_x = center_x + offset_x
            coin_y = start_y + offset_y
            
            # Shadow (only for bottom coin)
            if i == 0:
                shadow_rect = pygame.Rect(
                    coin_x - ellipse_width // 2 + 3,
                    coin_y + coin_thickness + 3,
                    ellipse_width,
                    ellipse_height
                )
                pygame.draw.ellipse(self.image, (0, 0, 0, 40), shadow_rect)
            
            # RIDGED EDGE (zigzag pattern on side)
            # Draw multiple thin vertical lines for ridged effect
            ridge_color = tuple(max(0, c - 60) for c in fill_color)
            num_ridges = 20
            
            for r in range(num_ridges):
                angle = (r / num_ridges) * 3.14159  # Half circle
                x_offset = int((ellipse_width // 2) * (1 - abs(angle - 1.57) / 1.57))
                
                # Left side ridges
                ridge_x = coin_x - ellipse_width // 2 + x_offset
                ridge_y1 = coin_y + ellipse_height // 2
                ridge_y2 = coin_y + coin_thickness + ellipse_height // 2
                
                if r % 2 == 0:  # Every other ridge is darker
                    pygame.draw.line(self.image, ridge_color, 
                                   (ridge_x, ridge_y1), (ridge_x, ridge_y2), 1)
            
            # Main cylinder body (gradient from dark to light)
            for y_offset in range(coin_thickness):
                progress = y_offset / coin_thickness
                body_color = tuple(
                    int(ridge_color[c] + (fill_color[c] - ridge_color[c]) * progress)
                    for c in range(3)
                )
                
                body_rect = pygame.Rect(
                    coin_x - ellipse_width // 2,
                    coin_y + ellipse_height // 2 + y_offset,
                    ellipse_width,
                    1
                )
                pygame.draw.ellipse(self.image, body_color, body_rect)
            
            # Bottom ellipse (darker edge)
            bottom_rect = pygame.Rect(
                coin_x - ellipse_width // 2,
                coin_y + coin_thickness,
                ellipse_width,
                ellipse_height
            )
            dark_edge = tuple(max(0, c - 40) for c in fill_color)
            pygame.draw.ellipse(self.image, dark_edge, bottom_rect)
            pygame.draw.ellipse(self.image, border_color, bottom_rect, 1)
            
            # Top ellipse (shiny gold surface)
            top_rect = pygame.Rect(
                coin_x - ellipse_width // 2,
                coin_y,
                ellipse_width,
                ellipse_height
            )
            
            # Gradient on top surface
            bright_gold = tuple(min(255, c + 30) for c in fill_color)
            pygame.draw.ellipse(self.image, bright_gold, top_rect)
            pygame.draw.ellipse(self.image, border_color, top_rect, 2)
            
            # Inner ring (embossed effect)
            inner_ring = top_rect.inflate(-ellipse_width // 4, -ellipse_height // 4)
            pygame.draw.ellipse(self.image, fill_color, inner_ring)
            pygame.draw.ellipse(self.image, border_color, inner_ring, 1)
            
            # Removed: White highlight/glow and sparkles per user request
            
    def update(self):
        # Simple floating animation?
        pass

    def trigger_sparkle(self):
        pass

class PiggyBankSprite(pygame.sprite.Sprite):
    def __init__(self, data, groups, grid_offsets=None, tile_size=TILE_SIZE):
        super().__init__(groups)
        self.data = data
        self.grid_x, self.grid_y = data['pos']
        self.tile_size = tile_size
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        self.color_key = data['color']
        self.current = data['current']
        self.capacity = data['capacity']
        
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # Position
        self.rect.x = self.offset_x + self.grid_x * self.tile_size
        self.rect.y = self.offset_y + self.grid_y * self.tile_size
        
        self.update_appearance()
        
    def update_appearance(self):
        self.image.fill((0,0,0,0))
        colors = BLOCK_COLORS.get(self.color_key, BLOCK_COLORS['YELLOW'])
        main_color = colors['main']
        dark_color = colors['dark']
        
        # Draw Container (Hollow box)
        rect = pygame.Rect(0, 0, self.tile_size, self.tile_size)
        pygame.draw.rect(self.image, main_color, rect, border_radius=8)
        
        # Inner dark area
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(self.image, dark_color, inner_rect, border_radius=4)
        
        # Draw "Glass" or Open front?
        # Just text for now
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.current}/{self.capacity}", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        self.image.blit(text, text_rect)

class ObstacleSprite(pygame.sprite.Sprite):
    def __init__(self, data, groups, grid_offsets=None, tile_size=TILE_SIZE):
        super().__init__(groups)
        self.grid_x, self.grid_y = data['pos']
        self.tile_size = tile_size
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        self.rect.x = self.offset_x + self.grid_x * self.tile_size
        self.rect.y = self.offset_y + self.grid_y * self.tile_size
        
        # Draw Gray Stone/Obstacle
        pygame.draw.rect(self.image, (100, 100, 100), (0, 0, self.tile_size, self.tile_size), border_radius=5)
        pygame.draw.rect(self.image, (150, 150, 150), (5, 5, self.tile_size-10, self.tile_size-10), border_radius=3)
        pygame.draw.line(self.image, (50,50,50), (0,0), (self.tile_size, self.tile_size), 2)
