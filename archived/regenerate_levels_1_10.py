#!/usr/bin/env python3
"""
Regenerate Levels 1-10 with Improved Difficulty and Tutorial
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from level_solver import solve_level

# Shape definitions
SHAPE_CELLS = {
    'I2': [(0, 0), (1, 0)],
    'I3': [(0, 0), (1, 0), (2, 0)],
    'I4': [(0, 0), (1, 0), (2, 0), (3, 0)],
    'O4': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'L3': [(0, 0), (1, 0), (0, 1)],
    'L4': [(0, 0), (1, 0), (2, 0), (0, 1)],
    'T4': [(0, 0), (1, 0), (2, 0), (1, 1)],
    'S4': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'Z4': [(0, 0), (1, 0), (1, 1), (2, 1)],
}

COLORS = ['red', 'blue', 'green', 'yellow', 'purple']

def generate_layout(width, height, wall_density=0.0):
    """Generate a grid layout with random walls"""
    layout = [[0 for _ in range(width)] for _ in range(height)]
    
    if wall_density > 0:
        num_walls = int(width * height * wall_density)
        for _ in range(num_walls):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            layout[y][x] = 1
    
    return layout

def find_empty_spots(layout):
    """Find all empty spots in layout"""
    empty = []
    for y in range(len(layout)):
        for x in range(len(layout[0])):
            if layout[y][x] == 0:
                empty.append((x, y))
    return empty

def can_place_shape(pos, shape, layout, occupied):
    """Check if a shape can be placed at position"""
    grid_w = len(layout[0])
    grid_h = len(layout)
    shape_cells = SHAPE_CELLS[shape]
    
    for dx, dy in shape_cells:
        x, y = pos[0] + dx, pos[1] + dy
        if x < 0 or x >= grid_w or y < 0 or y >= grid_h:
            return False
        if layout[y][x] == 1:
            return False
        if (x, y) in occupied:
            return False
    return True

def place_blocks(empty_spots, num_blocks, grid_w, grid_h, layout):
    """Place blocks randomly"""
    blocks = []
    occupied = set()
    shapes = list(SHAPE_CELLS.keys())
    
    for i in range(num_blocks):
        # Try to place a block
        for attempt in range(100):
            shape = random.choice(shapes)
            pos = random.choice(empty_spots)
            
            if can_place_shape(pos, shape, layout, occupied):
                color = COLORS[i % len(COLORS)]
                block = {
                    'id': f'b_{i}',
                    'shape': shape,
                    'color': color,
                    'counter': 0,  # Will be set later
                    'xy': list(pos)
                }
                blocks.append(block)
                
                # Mark cells as occupied
                for dx, dy in SHAPE_CELLS[shape]:
                    occupied.add((pos[0] + dx, pos[1] + dy))
                break
    
    return blocks if len(blocks) == num_blocks else None

def place_coins_for_blocks(blocks, empty_spots, coins_per_block, layout):
    """Place coins for each block"""
    coins = []
    occupied = set()
    
    # Mark block cells as occupied
    for block in blocks:
        for dx, dy in SHAPE_CELLS[block['shape']]:
            occupied.add((block['xy'][0] + dx, block['xy'][1] + dy))
    
    for block in blocks:
        color = block['color']
        placed = 0
        
        for attempt in range(200):
            pos = random.choice(empty_spots)
            if pos not in occupied:
                coins.append({'color': color, 'xy': list(pos)})
                occupied.add(pos)
                placed += 1
                if placed >= coins_per_block:
                    break
        
        if placed < coins_per_block:
            return None  # Failed to place enough coins
        
        block['counter'] = placed
    
    return coins

# Difficulty targets for first 10 levels
# Progressive difficulty with achievable targets
DIFFICULTY_TARGETS = {
    1:  {"blocks": 1, "coins_per_block": 3, "grid": (6,6), "walls": 0.00, "target_moves": (2, 6), "tutorial": "Drag the block to collect all coins! Match colors."},
    2:  {"blocks": 2, "coins_per_block": 3, "grid": (6,6), "walls": 0.00, "target_moves": (4, 10), "tutorial": "More blocks! Plan your moves carefully."},
    3:  {"blocks": 2, "coins_per_block": 3, "grid": (7,7), "walls": 0.00, "target_moves": (6, 12)},
    4:  {"blocks": 2, "coins_per_block": 4, "grid": (7,7), "walls": 0.05, "target_moves": (8, 16)},
    5:  {"blocks": 3, "coins_per_block": 3, "grid": (7,7), "walls": 0.05, "target_moves": (9, 18)},
    6:  {"blocks": 3, "coins_per_block": 3, "grid": (8,8), "walls": 0.08, "target_moves": (9, 20)},
    7:  {"blocks": 3, "coins_per_block": 4, "grid": (8,8), "walls": 0.08, "target_moves": (12, 24)},
    8:  {"blocks": 4, "coins_per_block": 3, "grid": (8,8), "walls": 0.10, "target_moves": (12, 26)},
    9:  {"blocks": 4, "coins_per_block": 3, "grid": (9,9), "walls": 0.10, "target_moves": (12, 28)},
    10: {"blocks": 4, "coins_per_block": 4, "grid": (9,9), "walls": 0.10, "target_moves": (16, 32)},
}

def create_level_with_target(level_num, target, max_attempts=100):
    """Internal function with recursion support"""
    num_blocks = target["blocks"]
    coins_per_block = target["coins_per_block"]
    grid_w, grid_h = target["grid"]
    wall_density = target["walls"]
    min_moves, max_moves = target["target_moves"]
    
    best_level = None
    best_moves = None
    best_distance = float('inf')
    
    for attempt in range(max_attempts):
        # Generate random level
        layout = generate_layout(grid_w, grid_h, wall_density)
        empty_spots = find_empty_spots(layout)
        
        if len(empty_spots) < num_blocks * 4 + num_blocks * coins_per_block:
            continue  # Not enough space
        
        # Place blocks
        blocks = place_blocks(empty_spots, num_blocks, grid_w, grid_h, layout)
        if not blocks:
            continue
        
        # Place coins
        coins = place_coins_for_blocks(blocks, empty_spots, coins_per_block, layout)
        if not coins:
            continue
        
        # Create level data
        level_data = {
            "meta": {
                "id": level_num,
                "world": 1,
                "name": f"Level {level_num}",
                "grid_size": [grid_w, grid_h],
                "time_limit": 60 + level_num * 10,
                "stars": [max_moves // 3, max_moves // 2, max_moves]
            },
            "layout": layout,
            "blocks": blocks,
            "coins": {"static": coins, "entrances": []}
        }
        
        # Add tutorial text if present
        if "tutorial" in target:
            level_data["tutorial_text"] = target["tutorial"]
        
        # Try to solve it
        is_solvable, solution, num_moves = solve_level(level_data, max_moves=max_moves + 15, verbose=False)
        
        if is_solvable:
            # Check if moves are in target range
            if min_moves <= num_moves <= max_moves:
                print(f"  ✅ Tentativo {attempt+1}: PERFETTO! {num_moves} mosse")
                return level_data, solution, num_moves
            
            # Track best attempt
            distance = abs(num_moves - (min_moves + max_moves) / 2)
            if distance < best_distance:
                best_distance = distance
                best_level = level_data
                best_moves = num_moves
        
    # If we found a solvable level (even if not perfect), use it
    if best_level:
        print(f"  ✅ Usando miglior tentativo: {best_moves} mosse (target: {min_moves}-{max_moves})")
        return best_level, None, best_moves
    
    print(f"  ⚠️  Target fallito per livello {level_num}, riprovo...")
    return None, None, 0

def regenerate_levels():
    """Regenerate levels 1-10"""
    print("=" * 60)
    print("RIGENERAZIONE LIVELLI 1-10 CON DIFFICOLTÀ AUMENTATA")
    print("=" * 60)
    
    for level_num in range(1, 11):
        print(f"Generazione Livello {level_num}...")
        target = DIFFICULTY_TARGETS[level_num]
        
        level_data = None
        while level_data is None:
            level_data, _, _ = create_level_with_target(level_num, target)
        
        # Save level
        filename = f"level_{level_num:03d}.json"
        filepath = os.path.join("data", "levels", filename)
        
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=2)
            
    print("\n✅ Livelli 1-10 rigenerati con successo!")
    print("=" * 60)

if __name__ == "__main__":
    regenerate_levels()
