"""
Test Level 3 - L-shaped block movement and coin collection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from core.level_loader import LevelLoader
from core.sprites import BlockSprite, CoinSprite, SHAPES
from core.grid_manager import GridManager
from core.settings import *

pygame.init()

# Load level 3
loader = LevelLoader()
level = loader.load_level(3)

print("=" * 60)
print("LEVEL 3 ANALYSIS")
print("=" * 60)

print(f"\nGrid: {level['grid_cols']}x{level['grid_rows']}")
print(f"\nLayout:")
for y, row in enumerate(level['layout']):
    print(f"Row {y}: {row}")

print(f"\nBlocks:")
for block_data in level['blocks']:
    print(f"  {block_data}")
    shape_name = block_data.get('shape', 'I2')
    shape_cells = SHAPES.get(shape_name, [(0, 0)])
    print(f"  Shape '{shape_name}' cells: {shape_cells}")
    
    start_x, start_y = block_data['start_pos']
    print(f"  Starting at ({start_x}, {start_y})")
    print(f"  Occupies grid cells:")
    for dx, dy in shape_cells:
        cell_x = start_x + dx
        cell_y = start_y + dy
        print(f"    ({cell_x}, {cell_y})")

print(f"\nCoins:")
for coin_data in level['coins']['static']:
    print(f"  {coin_data['color']} at {coin_data['pos']}")

# Test if block can reach all coins
print("\n" + "=" * 60)
print("REACHABILITY TEST")
print("=" * 60)

# Create grid manager
grid_manager = GridManager(level)

# Create block
block_data = level['blocks'][0]
block = BlockSprite(block_data, [])
grid_manager.register_block(block)

# Test movement to each coin
coins = level['coins']['static']
for i, coin_data in enumerate(coins):
    coin_pos = coin_data['pos']
    print(f"\nCoin {i+1}: {coin_data['color']} at {coin_pos}")
    
    # Check if block can occupy this position
    # For L4 shape at coin position, check all cells
    can_reach = True
    for dx, dy in block.shape_cells:
        check_x = coin_pos[0] + dx
        check_y = coin_pos[1] + dy
        
        # Check if valid
        if not (0 <= check_x < level['grid_cols'] and 0 <= check_y < level['grid_rows']):
            can_reach = False
            print(f"  ❌ Cell ({check_x}, {check_y}) is OUT OF BOUNDS")
            break
        
        # Check if wall
        if level['layout'][check_y][check_x] == 1:
            can_reach = False
            print(f"  ❌ Cell ({check_x}, {check_y}) is a WALL")
            break
    
    if can_reach:
        print(f"  ✓ Block CAN reach this coin")
    else:
        print(f"  ✗ Block CANNOT reach this coin")

# Test coin collection
print("\n" + "=" * 60)
print("COIN COLLECTION TEST")
print("=" * 60)

# Simulate placing block at coin position
test_coin = coins[0]
coin_x, coin_y = test_coin['pos']

print(f"\nTesting collection of coin at {test_coin['pos']}")
print(f"Block shape cells: {block.shape_cells}")
print(f"If block is at ({coin_x}, {coin_y}), it occupies:")

occupied = []
for dx, dy in block.shape_cells:
    cell = (coin_x + dx, coin_y + dy)
    occupied.append(cell)
    print(f"  {cell}")

print(f"\nCoin is at: {test_coin['pos']}")
if test_coin['pos'] in occupied:
    print("✓ Coin WILL be collected (overlaps with block)")
else:
    print("✗ Coin will NOT be collected (no overlap)")

print("\n" + "=" * 60)
print("SUGGESTED FIX")
print("=" * 60)

# Find valid positions for the block
print("\nSearching for valid positions where block can collect all coins...")

# For each coin, find if there's a block position where:
# 1. Block is valid (all cells in bounds and not walls)
# 2. Block overlaps the coin

for i, coin_data in enumerate(coins):
    coin_pos = coin_data['pos']
    print(f"\nCoin {i+1} at {coin_pos}:")
    
    found_positions = []
    # Try all possible block positions
    for bx in range(level['grid_cols']):
        for by in range(level['grid_rows']):
            # Check if block at (bx, by) can collect this coin
            valid = True
            overlaps_coin = False
            
            for dx, dy in block.shape_cells:
                cell_x = bx + dx
                cell_y = by + dy
                
                # Check bounds
                if not (0 <= cell_x < level['grid_cols'] and 0 <= cell_y < level['grid_rows']):
                    valid = False
                    break
                
                # Check wall
                if level['layout'][cell_y][cell_x] == 1:
                    valid = False
                    break
                
                # Check if overlaps coin
                if (cell_x, cell_y) == coin_pos:
                    overlaps_coin = True
            
            if valid and overlaps_coin:
                found_positions.append((bx, by))
    
    if found_positions:
        print(f"  ✓ Can be collected from {len(found_positions)} position(s):")
        for pos in found_positions[:3]:  # Show first 3
            print(f"    Block at {pos}")
    else:
        print(f"  ✗ CANNOT be collected from any position!")

pygame.quit()
