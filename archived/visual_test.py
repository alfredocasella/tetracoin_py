"""
Visual test to see the grid and block positioning
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from core.level_loader import LevelLoader
from core.sprites import BlockSprite
from core.settings import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Test")

loader = LevelLoader()
level = loader.load_level(1)

# Draw grid
screen.fill(BG_COLOR)

cols = level['grid_cols']
rows = level['grid_rows']

# Draw grid background
grid_width = cols * TILE_SIZE
grid_height = rows * TILE_SIZE
grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, grid_width, grid_height)
pygame.draw.rect(screen, (50, 50, 50), grid_rect)

# Draw cells
for row in range(rows):
    for col in range(cols):
        x = GRID_OFFSET_X + col * TILE_SIZE
        y = GRID_OFFSET_Y + row * TILE_SIZE
        
        cell_value = level['layout'][row][col]
        
        if cell_value == 1:  # Wall
            pygame.draw.rect(screen, WALL_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
        else:  # Empty
            pygame.draw.rect(screen, EMPTY_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
        
        # Draw grid lines
        pygame.draw.rect(screen, GRID_LINE_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)

# Draw border
pygame.draw.rect(screen, (255, 255, 255), grid_rect, 3)

# Draw block
block_sprites = pygame.sprite.Group()
for block_data in level['blocks']:
    block = BlockSprite(block_data, [block_sprites])

block_sprites.draw(screen)

# Add labels
font = pygame.font.SysFont(None, 24)
text = font.render(f"Grid: {cols}x{rows}, Offset: ({GRID_OFFSET_X},{GRID_OFFSET_Y}), Tile: {TILE_SIZE}", True, (255, 255, 255))
screen.blit(text, (10, 10))

pygame.display.flip()

# Save screenshot
pygame.image.save(screen, "grid_test.png")
print("Screenshot saved as grid_test.png")
print(f"Grid: {cols}x{rows}")
print(f"Grid bounds: ({GRID_OFFSET_X}, {GRID_OFFSET_Y}) to ({GRID_OFFSET_X + grid_width}, {GRID_OFFSET_Y + grid_height})")
print("Close the window to exit")

# Wait for close
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
