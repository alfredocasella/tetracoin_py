#!/usr/bin/env python3
"""
Automated Level Testing Script
Verifies level JSON files for structural correctness and constraint compliance.
"""

import json
import os
import sys

# Shape definitions (same as in level_generator.py)
SHAPE_CELLS = {
    "I2": [(0, 0), (1, 0)],
    "I3": [(0, 0), (1, 0), (2, 0)],
    "I4": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "L4": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "J4": [(1, 0), (1, 1), (1, 2), (0, 2)],
    "O4": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T4": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S4": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z4": [(0, 0), (1, 0), (1, 1), (2, 1)],
}

def can_block_reach_position(block_pos, block_shape, target_pos, layout, grid_w, grid_h, other_blocks):
    """Use BFS to check if a block can reach a target position"""
    from collections import deque
    
    shape_cells = SHAPE_CELLS.get(block_shape, [(0, 0)])
    start = tuple(block_pos)
    target = tuple(target_pos)
    
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        current_pos = queue.popleft()
        
        # Check if block at current position overlaps target
        for dx, dy in shape_cells:
            cell_x = current_pos[0] + dx
            cell_y = current_pos[1] + dy
            if (cell_x, cell_y) == target:
                return True
        
        # Try all 4 directions
        for move_dx, move_dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = current_pos[0] + move_dx
            new_y = current_pos[1] + move_dy
            new_pos = (new_x, new_y)
            
            if new_pos in visited:
                continue
            
            # Check if all cells of the block fit and are valid
            valid_move = True
            for dx, dy in shape_cells:
                cell_x = new_x + dx
                cell_y = new_y + dy
                
                # Check bounds
                if not (0 <= cell_x < grid_w and 0 <= cell_y < grid_h):
                    valid_move = False
                    break
                
                # Check walls
                if layout[cell_y][cell_x] == 1:
                    valid_move = False
                    break
                
                # Check collision with other blocks
                if (cell_x, cell_y) in other_blocks:
                    valid_move = False
                    break
            
            if valid_move:
                visited.add(new_pos)
                queue.append(new_pos)
    
    return False


def test_level(level_num):
    """Test a single level file"""
    filepath = f"data/levels/level_{level_num:03d}.json"
    
    if not os.path.exists(filepath):
        return {"level": level_num, "status": "MISSING", "errors": [f"File not found: {filepath}"]}
    
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"level": level_num, "status": "INVALID_JSON", "errors": [str(e)]}
    
    # Check meta
    if 'meta' not in data:
        errors.append("Missing 'meta' section")
    else:
        meta = data['meta']
        if meta.get('id') != level_num:
            errors.append(f"Meta ID mismatch: expected {level_num}, got {meta.get('id')}")
        
        if 'grid_size' not in meta:
            errors.append("Missing 'grid_size' in meta")
        
        if 'time_limit' not in meta:
            errors.append("Missing 'time_limit' in meta")
    
    # Check layout
    if 'layout' not in data:
        errors.append("Missing 'layout'")
    else:
        layout = data['layout']
        grid_h = len(layout)
        grid_w = len(layout[0]) if grid_h > 0 else 0
        
        # Verify grid size matches meta
        if 'meta' in data and 'grid_size' in data['meta']:
            expected_w, expected_h = data['meta']['grid_size']
            if grid_w != expected_w or grid_h != expected_h:
                errors.append(f"Layout size mismatch: expected {expected_w}x{expected_h}, got {grid_w}x{grid_h}")
        
        # Check for perimeter walls (should be all 0 on edges)
        has_perimeter_walls = False
        if grid_h > 0 and grid_w > 0:
            # Top row
            if any(cell == 1 for cell in layout[0]):
                has_perimeter_walls = True
            # Bottom row
            if any(cell == 1 for cell in layout[-1]):
                has_perimeter_walls = True
            # Left column
            if any(row[0] == 1 for row in layout):
                has_perimeter_walls = True
            # Right column
            if any(row[-1] == 1 for row in layout):
                has_perimeter_walls = True
        
        if has_perimeter_walls:
            warnings.append("Perimeter walls detected (edges should be playable)")
    
    # Check blocks
    if 'blocks' not in data:
        errors.append("Missing 'blocks'")
    else:
        blocks = data['blocks']
        if not isinstance(blocks, list):
            errors.append("'blocks' should be a list")
        else:
            # Track occupied cells by each block
            all_block_cells = {}  # block_id -> set of (x, y)
            
            for i, block in enumerate(blocks):
                block_id = block.get('id', f'block_{i}')
                
                if 'xy' not in block:
                    errors.append(f"Block {block_id} missing 'xy' position")
                    continue
                if 'color' not in block:
                    errors.append(f"Block {block_id} missing 'color'")
                if 'counter' not in block:
                    errors.append(f"Block {block_id} missing 'counter'")
                if 'shape' not in block:
                    errors.append(f"Block {block_id} missing 'shape'")
                    continue
                
                # Check if block position is within bounds
                block_pos = block['xy']
                if 'layout' in data:
                    grid_h = len(data['layout'])
                    grid_w = len(data['layout'][0]) if grid_h > 0 else 0
                    
                    if not (0 <= block_pos[0] < grid_w and 0 <= block_pos[1] < grid_h):
                        errors.append(f"Block {block_id} position {block_pos} is outside grid bounds (0-{grid_w-1}, 0-{grid_h-1})")
                
                # Calculate actual cells occupied by this block
                shape = block['shape']
                pos = block['xy']
                shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
                
                occupied = set()
                for dx, dy in shape_cells:
                    cell_x = pos[0] + dx
                    cell_y = pos[1] + dy
                    occupied.add((cell_x, cell_y))
                
                all_block_cells[block_id] = occupied
                
                # Check if block fits in grid
                if 'layout' in data:
                    grid_h = len(data['layout'])
                    grid_w = len(data['layout'][0]) if grid_h > 0 else 0
                    
                    for cell_x, cell_y in occupied:
                        if not (0 <= cell_x < grid_w and 0 <= cell_y < grid_h):
                            errors.append(f"Block {block_id} extends outside grid at ({cell_x}, {cell_y})")
    
    # Check coins
    coin_counts_by_color = {}  # color -> count
    all_coin_positions = []  # list of [x, y]
    
    if 'coins' not in data:
        errors.append("Missing 'coins'")
    else:
        coins_data = data['coins']
        if 'static' not in coins_data:
            errors.append("Missing 'coins.static'")
        else:
            static_coins = coins_data['static']
            
            for coin in static_coins:
                if 'xy' not in coin:
                    errors.append("Coin missing 'xy' position")
                    continue
                if 'color' not in coin:
                    errors.append("Coin missing 'color'")
                    continue
                
                coin_pos = coin['xy']
                coin_color = coin['color']
                
                # Check if coin position is within bounds
                if 'layout' in data:
                    grid_h = len(data['layout'])
                    grid_w = len(data['layout'][0]) if grid_h > 0 else 0
                    
                    if not (0 <= coin_pos[0] < grid_w and 0 <= coin_pos[1] < grid_h):
                        errors.append(f"Coin at {coin_pos} is outside grid bounds (0-{grid_w-1}, 0-{grid_h-1})")
                
                # Track coin count by color
                coin_counts_by_color[coin_color] = coin_counts_by_color.get(coin_color, 0) + 1
                
                # Check for duplicate coins at same position
                if coin_pos in all_coin_positions:
                    errors.append(f"Duplicate coin at position {coin_pos}")
                all_coin_positions.append(coin_pos)
                
                # Check for overlaps with blocks
                if 'blocks' in data:
                    for block_id, occupied in all_block_cells.items():
                        if tuple(coin_pos) in occupied:
                            errors.append(f"Coin at {coin_pos} overlaps with block {block_id}")
    
    # Verify each block has correct number of coins
    if 'blocks' in data and isinstance(data['blocks'], list):
        for block in data['blocks']:
            if 'color' in block and 'counter' in block:
                block_color = block['color']
                expected_count = block['counter']
                actual_count = coin_counts_by_color.get(block_color, 0)
                
                if actual_count != expected_count:
                    errors.append(f"Block color '{block_color}' expects {expected_count} coins but has {actual_count}")
    
    # Verify solvability: each block can reach at least one of its coins
    if 'blocks' in data and 'coins' in data and 'layout' in data:
        layout = data['layout']
        grid_h = len(layout)
        grid_w = len(layout[0]) if grid_h > 0 else 0
        
        # Build set of all block cells (for collision detection)
        all_other_blocks = {}
        for block in data['blocks']:
            block_id = block.get('id', 'unknown')
            if 'shape' in block and 'xy' in block:
                shape = block['shape']
                pos = block['xy']
                shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
                
                cells = set()
                for dx, dy in shape_cells:
                    cells.add((pos[0] + dx, pos[1] + dy))
                all_other_blocks[block_id] = cells
        
        # Check each block
        for block in data['blocks']:
            if 'color' not in block or 'shape' not in block or 'xy' not in block:
                continue
            
            block_id = block.get('id', 'unknown')
            block_color = block['color']
            block_shape = block['shape']
            block_pos = block['xy']
            
            # Get all coins of this color
            matching_coins = [coin['xy'] for coin in data['coins']['static'] if coin.get('color') == block_color]
            
            if not matching_coins:
                continue
            
            # Build other_blocks set (excluding current block)
            other_blocks = set()
            for other_id, cells in all_other_blocks.items():
                if other_id != block_id:
                    other_blocks.update(cells)
            
            # Check if block can reach at least one coin
            can_reach_any = False
            for coin_pos in matching_coins:
                if can_block_reach_position(block_pos, block_shape, coin_pos, layout, grid_w, grid_h, other_blocks):
                    can_reach_any = True
                    break
            
            if not can_reach_any:
                errors.append(f"Block {block_id} ({block_color}) cannot reach any of its coins - UNSOLVABLE")
    
    # Determine status
    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARN"
    else:
        status = "PASS"
    
    return {
        "level": level_num,
        "status": status,
        "errors": errors,
        "warnings": warnings
    }

def main():
    """Run tests on levels 1-20"""
    print("=" * 60)
    print("TetraCoin Level Testing - Levels 1-20")
    print("=" * 60)
    print()
    
    results = []
    for level_num in range(1, 21):
        result = test_level(level_num)
        results.append(result)
        
        # Print result
        status_symbol = {
            "PASS": "✓",
            "WARN": "⚠",
            "FAIL": "✗",
            "MISSING": "?",
            "INVALID_JSON": "✗"
        }.get(result['status'], "?")
        
        print(f"Level {level_num:2d}: {status_symbol} {result['status']}")
        
        if result['errors']:
            for error in result['errors']:
                print(f"  ERROR: {error}")
        
        if result.get('warnings'):
            for warning in result['warnings']:
                print(f"  WARN: {warning}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    warn_count = sum(1 for r in results if r['status'] == 'WARN')
    fail_count = sum(1 for r in results if r['status'] in ['FAIL', 'MISSING', 'INVALID_JSON'])
    
    print(f"PASS: {pass_count}")
    print(f"WARN: {warn_count}")
    print(f"FAIL: {fail_count}")
    print()
    
    if fail_count > 0:
        print("❌ Some levels have ERRORS that need to be fixed!")
        sys.exit(1)
    elif warn_count > 0:
        print("⚠️  All levels functional but some have warnings")
        sys.exit(0)
    else:
        print("✅ All levels PASS!")
        sys.exit(0)

if __name__ == "__main__":
    main()
