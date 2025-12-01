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
    # Class-level cache for base sprite
    _base_sprite = None
    
    def __init__(self, coin_data, groups, grid_offsets=None):
        super().__init__(groups)
        self.coin_data = coin_data
        self.grid_x, self.grid_y = coin_data['pos']
        self.color = COLORS.get(coin_data['color'], (255, 215, 0))
        
        # Use provided offsets or fallback to settings
        self.offset_x = grid_offsets[0] if grid_offsets else GRID_OFFSET_X
        self.offset_y = grid_offsets[1] if grid_offsets else GRID_OFFSET_Y
        
        self.base_size = TILE_SIZE
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # Set initial position with Y offset for 3D effect
        y_offset = -4  # Slightly above cell for stacked effect
        self.rect.x = self.offset_x + self.grid_x * TILE_SIZE
        self.rect.y = self.offset_y + self.grid_y * TILE_SIZE + y_offset
        
        # Animation state
        self.original_y = self.rect.y
        self.pulse_time = 0
        self.sparkle_timer = 0
        
        # Load and apply color tinting
        self._apply_color_tint()
        
    def _load_base_sprite(self):
        """Load the greyscale base sprite (cached at class level)"""
        if CoinSprite._base_sprite is None:
            asset_path = os.path.join(os.path.dirname(__file__), 'assets', 'coin_stack_base.png')
            
            if os.path.exists(asset_path):
                # Load from PNG
                loaded_sprite = pygame.image.load(asset_path).convert_alpha()
                CoinSprite._base_sprite = pygame.transform.scale(loaded_sprite, (self.base_size, self.base_size))
            else:
                # Fallback: generate procedurally if asset doesn't exist
                print(f"Warning: {asset_path} not found, generating procedurally")
                CoinSprite._base_sprite = self._generate_greyscale_sprite()
                
        return CoinSprite._base_sprite
    
    def _generate_greyscale_sprite(self):
        """Fallback: Generate greyscale sprite procedurally"""
        sprite = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        sprite.fill((0, 0, 0, 0))
        
        center_x = self.base_size // 2
        disc_radius = (self.base_size - 8) // 2
        num_discs = 6
        disc_thickness = 2
        disc_spacing = 2
        base_y = self.base_size - 4
        
        # Greyscale colors
        light_grey = (200, 200, 200)
        dark_grey = (100, 100, 100)
        white = (255, 255, 255)
        
        # Shadow
        shadow_rect = pygame.Rect(center_x - disc_radius - 1, base_y + 1,
                                  disc_radius * 2 + 2, 4)
        pygame.draw.ellipse(sprite, (40, 40, 40, 150), shadow_rect)
        
        # Draw discs
        for i in range(num_discs):
            disc_y = base_y - (i * (disc_thickness + disc_spacing))
            
            # Edge
            edge_rect = pygame.Rect(center_x - disc_radius, disc_y,
                                   disc_radius * 2, disc_thickness)
            pygame.draw.rect(sprite, dark_grey, edge_rect)
            pygame.draw.circle(sprite, dark_grey,
                             (center_x - disc_radius, disc_y + disc_thickness // 2),
                             disc_thickness // 2)
            pygame.draw.circle(sprite, dark_grey,
                             (center_x + disc_radius, disc_y + disc_thickness // 2),
                             disc_thickness // 2)
            
            # Top face
            top_y = disc_y - 1
            top_rect = pygame.Rect(center_x - disc_radius, top_y,
                                  disc_radius * 2, disc_thickness + 2)
            pygame.draw.ellipse(sprite, light_grey, top_rect)
            pygame.draw.ellipse(sprite, white, top_rect, 1)
        
        return sprite
    
    def _apply_color_tint(self):
        """Apply color tint to greyscale base sprite"""
        # Load base sprite
        base_sprite = self._load_base_sprite()
        
        # Create tinted version
        self.image = base_sprite.copy()
        
        # Get tint color from coin data
        color_key = self.coin_data['color']
        colors = COIN_COLORS.get(color_key, COIN_COLORS['YELLOW'])
        tint_color = colors['fill']
        
        # Apply tint using RGBA multiply blend
        # Create a tint surface
        tint_surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        tint_surface.fill((*tint_color, 255))
        
        # Apply multiplicative blend to tint the sprite
        self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
    def update(self):
        # Static coin - no animations for now
        # Sparkle effects removed for simplicity with tinting system
        pass

    def trigger_sparkle(self):
        # Placeholder for future animation
        pass
