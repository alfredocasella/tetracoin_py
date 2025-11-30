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
        fill_color = colors['fill']
        border_color = colors['border']
        
        # Draw each cell as a separate rounded rect with gaps
        # Prototype uses (cellSize + 4) spacing.
        # Our TILE_SIZE includes the gap.
        # So we should draw the cell smaller than TILE_SIZE.
        
        gap = 4
        cell_size = TILE_SIZE - gap
        offset = gap // 2
        
        for dx, dy in self.shape_cells:
            cell_x = dx * TILE_SIZE + offset
            cell_y = dy * TILE_SIZE + offset
            
            # Main Body (Rounded Rect)
            rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            
            # Draw Fill
            pygame.draw.rect(self.image, fill_color, rect, border_radius=8)
            
            # Draw Border (Inset)
            pygame.draw.rect(self.image, border_color, rect, 3, border_radius=8)
            
            # Top Highlight
            highlight_rect = pygame.Rect(cell_x + 3, cell_y + 3, cell_size - 6, cell_size // 2 - 3)
            s = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            s.fill((255, 255, 255, 40))
            self.image.blit(s, highlight_rect)
            
            # Bottom Shadow
            shadow_rect = pygame.Rect(cell_x + 3, cell_y + cell_size // 2, cell_size - 6, cell_size // 2 - 3)
            s = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 20))
            self.image.blit(s, shadow_rect)

        # Draw Counter (Badge style)
        min_x = min(c[0] for c in self.shape_cells)
        max_x = max(c[0] for c in self.shape_cells)
        min_y = min(c[1] for c in self.shape_cells)
        max_y = max(c[1] for c in self.shape_cells)
        
        center_x = (min_x + max_x + 1) * TILE_SIZE / 2
        center_y = (min_y + max_y + 1) * TILE_SIZE / 2
        
        if self.counter > 0:
            font = pygame.font.SysFont("Arial", 24, bold=True)
            text_surf = font.render(str(self.counter), True, (26, 33, 48)) # Dark text
            
            # Badge background
            badge_size = int(TILE_SIZE * 0.6)
            badge_rect = pygame.Rect(0, 0, badge_size, badge_size)
            badge_rect.center = (center_x, center_y)
            
            # White circle with border
            pygame.draw.circle(self.image, (255, 255, 255), badge_rect.center, badge_size // 2)
            pygame.draw.circle(self.image, border_color, badge_rect.center, badge_size // 2, 2)
            
            # If counter is 1, fill with light color
            if self.counter == 1:
                s = pygame.Surface((badge_size, badge_size), pygame.SRCALPHA)
                pygame.draw.circle(s, (*fill_color, 200), (badge_size//2, badge_size//2), badge_size // 2)
                self.image.blit(s, badge_rect)
            
            text_rect = text_surf.get_rect(center=badge_rect.center)
            self.image.blit(text_surf, text_rect)

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
