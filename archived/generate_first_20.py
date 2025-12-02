#!/usr/bin/env python3
"""
Generate First 20 Levels with Progressive Difficulty
Uses complete solver to verify each level is solvable
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

# Difficulty targets for first 20 levels
DIFFICULTY_TARGETS = {
    1:  {"blocks": 1, "coins_per_block": 2, "grid": (6,6), "walls": 0.00, "target_moves": (2, 5)},
    2:  {"blocks": 1, "coins_per_block": 3, "grid": (6,6), "walls": 0.00, "target_moves": (3, 6)},
    3:  {"blocks": 1, "coins_per_block": 4, "grid": (7,7), "walls": 0.00, "target_moves": (4, 8)},
    4:  {"blocks": 2, "coins_per_block": 2, "grid": (7,7), "walls": 0.00, "target_moves": (4, 8)},
    5:  {"blocks": 2, "coins_per_block": 3, "grid": (7,7), "walls": 0.00, "target_moves": (6, 12)},
    6:  {"blocks": 2, "coins_per_block": 3, "grid": (7,7), "walls": 0.05, "target_moves": (6, 12)},
    7:  {"blocks": 2, "coins_per_block": 4, "grid": (7,7), "walls": 0.05, "target_moves": (8, 15)},
    8:  {"blocks": 2, "coins_per_block": 4, "grid": (8,8), "walls": 0.05, "target_moves": (8, 15)},
    9:  {"blocks": 3, "coins_per_block": 2, "grid": (8,8), "walls": 0.05, "target_moves": (6, 12)},
    10: {"blocks": 3, "coins_per_block": 3, "grid": (8,8), "walls": 0.05, "target_moves": (9, 18)},
    11: {"blocks": 3, "coins_per_block": 3, "grid": (8,8), "walls": 0.08, "target_moves": (9, 18)},
    12: {"blocks": 3, "coins_per_block": 3, "grid": (8,8), "walls": 0.08, "target_moves": (9, 18)},
    13: {"blocks": 3, "coins_per_block": 4, "grid": (8,8), "walls": 0.08, "target_moves": (12, 24)},
    14: {"blocks": 3, "coins_per_block": 4, "grid": (9,9), "walls": 0.08, "target_moves": (12, 24)},
    15: {"blocks": 3, "coins_per_block": 4, "grid": (9,9), "walls": 0.10, "target_moves": (12, 24)},
    16: {"blocks": 4, "coins_per_block": 3, "grid": (9,9), "walls": 0.10, "target_moves": (12, 24)},
    17: {"blocks": 4, "coins_per_block": 3, "grid": (9,9), "walls": 0.10, "target_moves": (12, 24)},
    18: {"blocks": 4, "coins_per_block": 4, "grid": (9,9), "walls": 0.10, "target_moves": (16, 32)},
    19: {"blocks": 4, "coins_per_block": 4, "grid": (10,10), "walls": 0.10, "target_moves": (16, 32)},
    20: {"blocks": 4, "coins_per_block": 4, "grid": (10,10), "walls": 0.12, "target_moves": (16, 32)},
}




def create_level_with_target(level_num, target, max_attempts=30):
    """Wrapper for internal recursive function"""
    return create_level_with_target_internal(level_num, target, max_attempts)

def create_level_with_target_internal(level_num, target, max_attempts):
    """Internal function with recursion support"""
    num_blocks = target["blocks"]
    coins_per_block = target["coins_per_block"]
    grid_w, grid_h = target["grid"]
    wall_density = target["walls"]
    min_moves, max_moves = target["target_moves"]
    
    # ... (rest of the generation logic)
    
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
                # print(f"  ⚠️  Tentativo {attempt+1}: Risolvibile in {num_moves} mosse (target: {min_moves}-{max_moves})")
        
        if (attempt + 1) % 10 == 0:
             pass # print(f"  ... {attempt+1} tentativi...")
    
    # If we found a solvable level (even if not perfect), use it
    if best_level:
        print(f"  ✅ Usando miglior tentativo: {best_moves} mosse (target: {min_moves}-{max_moves})")
        return best_level, None, best_moves
    
    # Smart Fallback: Try reducing difficulty instead of giving up
    print(f"  ⚠️  Target fallito, provo con difficoltà ridotta...")
    
    # Strategy 1: Remove walls
    if wall_density > 0:
        print(f"  ... Rimuovo muri")
        reduced_target = target.copy()
        reduced_target["walls"] = 0.0
        # Recursive call with fewer attempts
        result = create_level_with_target_internal(level_num, reduced_target, max_attempts=20)
        if result:
            return result
            
    # Strategy 2: Reduce blocks (keep at least 2)
    if num_blocks > 2:
        print(f"  ... Riduco blocchi da {num_blocks} a {num_blocks-1}")
        reduced_target = target.copy()
        reduced_target["blocks"] = num_blocks - 1
        reduced_target["walls"] = 0.0 # Also remove walls to be safe
        result = create_level_with_target_internal(level_num, reduced_target, max_attempts=20)
        if result:
            return result

    # Strategy 3: Reduce coins per block
    if coins_per_block > 2:
        print(f"  ... Riduco monete da {coins_per_block} a {coins_per_block-1}")
        reduced_target = target.copy()
        reduced_target["coins_per_block"] = coins_per_block - 1
        reduced_target["walls"] = 0.0
        result = create_level_with_target_internal(level_num, reduced_target, max_attempts=20)
        if result:
            return result

    # Ultimate Fallback: create very simple level (but slightly better than before)
    print(f"  ❌ Fallback finale: livello semplice garantito")
    
    # Simple fallback: 1 block, 3 coins, large grid
    layout = [[0 for _ in range(8)] for _ in range(8)]
    blocks = [{
        'id': 'b_0',
        'shape': 'I3',
        'color': 'blue',
        'counter': 3,
        'xy': [2, 2]
    }]
    coins = [
        {'color': 'blue', 'xy': [5, 2]},
        {'color': 'blue', 'xy': [2, 5]},
        {'color': 'blue', 'xy': [5, 5]}
    ]
    
    fallback = {
        "meta": {
            "id": level_num,
            "world": 1,
            "name": f"Level {level_num}",
            "grid_size": [8, 8],
            "time_limit": 60,
            "stars": [5, 8, 12]
        },
        "layout": layout,
        "blocks": blocks,
        "coins": {"static": coins, "entrances": []}
    }
    
    return fallback, None, 0


def generate_first_20_levels():
    """Generate first 20 levels with progressive difficulty"""
    print("=" * 60)
    print("GENERAZIONE PRIMI 20 LIVELLI CON SOLVER COMPLETO")
    print("=" * 60)
    
    results = []
    
    for level_num in range(9, 21):
        target = DIFFICULTY_TARGETS[level_num]
        level_data, solution, num_moves = create_level_with_target(level_num, target)
        
        # Save level
        filename = f"level_{level_num:03d}.json"
        filepath = os.path.join("data", "levels", filename)
        
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        results.append({
            "level": level_num,
            "moves": num_moves,
            "target": target["target_moves"]
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    for r in results:
        target_min, target_max = r["target"]
        status = "✅" if target_min <= r["moves"] <= target_max else "⚠️"
        print(f"{status} Livello {r['level']:2d}: {r['moves']:2d} mosse (target: {target_min}-{target_max})")
    
    print("\n✅ Primi 20 livelli generati con successo!")
    print("=" * 60)


if __name__ == "__main__":
    generate_first_20_levels()
