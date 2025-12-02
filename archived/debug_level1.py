"""
Quick test to verify Level 1 block positioning
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from core.level_loader import LevelLoader
from core.sprites import BlockSprite, SHAPES
from core.settings import *

pygame.init()

# Load level 1
loader = LevelLoader()
level = loader.load_level(1)

print(f"Level 1: {level['grid_cols']}x{level['grid_rows']} grid")
print(f"Grid offset: ({GRID_OFFSET_X}, {GRID_OFFSET_Y})")
print(f"Tile size: {TILE_SIZE}")

for block_data in level['blocks']:
    print(f"\nBlock: {block_data}")
    shape_name = block_data.get('shape', 'I2')
    shape_cells = SHAPES.get(shape_name, [(0, 0)])
    start_x, start_y = block_data['start_pos']
    
    print(f"Shape '{shape_name}' cells: {shape_cells}")
    print(f"Starting at ({start_x}, {start_y})")
    print(f"Occupies grid cells:")
    
    for dx, dy in shape_cells:
        cell_x = start_x + dx
        cell_y = start_y + dy
        pixel_x = GRID_OFFSET_X + cell_x * TILE_SIZE
        pixel_y = GRID_OFFSET_Y + cell_y * TILE_SIZE
        
        in_bounds = (0 <= cell_x < level['grid_cols'] and 
                    0 <= cell_y < level['grid_rows'])
        
        print(f"  ({cell_x}, {cell_y}) -> pixels ({pixel_x}, {pixel_y}) - {'OK' if in_bounds else 'OUT OF BOUNDS!'}")

# Calculate block visual bounds
block_data = level['blocks'][0]
shape_cells = SHAPES.get(block_data.get('shape', 'I2'), [(0, 0)])
max_x = max(cell[0] for cell in shape_cells)
max_y = max(cell[1] for cell in shape_cells)
width = (max_x + 1) * TILE_SIZE
height = (max_y + 1) * TILE_SIZE

start_x, start_y = block_data['start_pos']
visual_x = GRID_OFFSET_X + start_x * TILE_SIZE
visual_y = GRID_OFFSET_Y + start_y * TILE_SIZE

print(f"\nBlock visual bounds:")
print(f"  Position: ({visual_x}, {visual_y})")
print(f"  Size: {width}x{height}")
print(f"  Right edge: {visual_x + width}")
print(f"  Bottom edge: {visual_y + height}")
print(f"  Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
