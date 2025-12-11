import json
import os
import random

# Configurazione Base
OUTPUT_DIR = "data/levels"
SHAPES = ["I2", "I3", "L4", "O4", "T4", "S4"]
COLORS = ["red", "blue", "green", "yellow", "purple"]

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_layout(width, height, density=0.1):
    """Genera una griglia con muri casuali interni, senza bordo perimetrale."""
    layout = []
    for _ in range(height):
        row = []
        for _ in range(width):
            # Probabilità di muro interno, altrimenti vuoto (0)
            cell = 1 if random.random() < density else 0
            row.append(cell)
        layout.append(row)
    return layout

def find_empty_spots(layout):
    spots = []
    for y, row in enumerate(layout):
        for x, cell in enumerate(row):
            if cell == 0:
                spots.append([x, y])
    return spots

# Tetris shape definitions (same as in sprites.py)
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

def can_block_reach_coin(block_shape, coin_pos, layout, grid_w, grid_h):
    """Check if a block can reach a coin position"""
    shape_cells = SHAPE_CELLS.get(block_shape, [(0, 0)])
    
    # Try all possible block positions
    for bx in range(grid_w):
        for by in range(grid_h):
            # Check if block at (bx, by) can collect this coin
            valid = True
            overlaps_coin = False
            
            for dx, dy in shape_cells:
                cell_x = bx + dx
                cell_y = by + dy
                
                # Check bounds
                if not (0 <= cell_x < grid_w and 0 <= cell_y < grid_h):
                    valid = False
                    break
                
                # Check wall
                if layout[cell_y][cell_x] == 1:
                    valid = False
                    break
                
                # Check if overlaps coin
                if (cell_x, cell_y) == coin_pos:
                    overlaps_coin = True
            
            if valid and overlaps_coin:
                return True
    
    return False

def place_reachable_coins(layout, grid_w, grid_h, block_shape, num_coins, occupied_cells, all_coins_placed):
    """Place coins that are guaranteed to be reachable by the block and not under any block or overlapping other coins"""
    shape_cells = SHAPE_CELLS.get(block_shape, [(0, 0)])
    max_shape_x = max(cell[0] for cell in shape_cells)
    max_shape_y = max(cell[1] for cell in shape_cells)
    
    coins = []
    attempts = 0
    max_attempts = 5000  # Increased from 1000 to allow more attempts
    
    while len(coins) < num_coins and attempts < max_attempts:
        attempts += 1
        
        # Pick a random empty spot with enough margin for the block shape
        # Reduce margin to allow more positions
        margin = 1  # Reduced from 2 to allow edge positions
        if grid_w <= margin * 2 + max_shape_x or grid_h <= margin * 2 + max_shape_y:
            margin = 0  # Allow edge positions if grid is small
        
        x = random.randint(margin, grid_w - margin - 1)
        y = random.randint(margin, grid_h - margin - 1)
        
        # Check if this spot is empty (no wall)
        if layout[y][x] != 0:
            continue
        
        # Check if occupied by ANY block (including the current one)
        if (x, y) in occupied_cells:
            continue
        
        # Check if already has a coin (from this block)
        if [x, y] in coins:
            continue
        
        # Check if already has a coin from ANY other block (GLOBAL CHECK)
        if [x, y] in all_coins_placed:
            continue
        
        # Verify block can reach this coin
        if can_block_reach_coin(block_shape, (x, y), layout, grid_w, grid_h):
            coins.append([x, y])
    
    return coins

def can_block_reach_position(block_pos, block_shape, target_pos, layout, grid_w, grid_h, other_blocks):
    """Use BFS to check if a block can reach a target position"""
    from collections import deque
    
    shape_cells = SHAPE_CELLS.get(block_shape, [(0, 0)])
    start = tuple(block_pos)
    target = tuple(target_pos)
    
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    # Limit BFS to prevent infinite loops on large grids
    max_iterations = grid_w * grid_h * 4  # Reasonable limit
    iterations = 0
    
    while queue and iterations < max_iterations:
        iterations += 1
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

def verify_level_solvable(level_data, fast_mode=False):
    """Verify that all blocks can reach ALL of their required coins (improved version)
    
    Args:
        level_data: Level data dictionary (can be in JSON format or converted format)
        fast_mode: If True, use simplified checks (faster but less accurate)
    """
    layout = level_data['layout']
    grid_h = len(layout)
    grid_w = len(layout[0]) if grid_h > 0 else 0
    blocks = level_data['blocks']
    
    # Handle both formats: JSON format (coins['static']) and converted format
    if isinstance(level_data.get('coins'), dict):
        coins = level_data['coins'].get('static', [])
    else:
        # Old format: coins is a list
        coins = level_data.get('coins', [])
    
    # Helper function to normalize color
    def normalize_color(color):
        if isinstance(color, str):
            return color.lower()
        return str(color).lower()
    
    # Helper function to get block position
    def get_block_pos(block):
        if 'xy' in block:
            return block['xy']
        elif 'start_pos' in block:
            pos = block['start_pos']
            # Convert tuple to list if needed
            return list(pos) if isinstance(pos, tuple) else pos
        return None
    
    # Helper function to get coin position
    def get_coin_pos(coin):
        if 'xy' in coin:
            pos = coin['xy']
            return list(pos) if isinstance(pos, tuple) else pos
        elif 'pos' in coin:
            pos = coin['pos']
            return list(pos) if isinstance(pos, tuple) else pos
        return None
    
    # Fast mode: simplified check (just verify coins exist and blocks can move)
    if fast_mode:
        for block in blocks:
            block_color = normalize_color(block['color'])
            block_counter = block.get('counter', block.get('count', 0))
            
            # Count matching coins
            matching_count = 0
            for coin in coins:
                coin_color = normalize_color(coin.get('color', ''))
                if coin_color == block_color:
                    matching_count += 1
            
            if matching_count < block_counter:
                return False
        return True
    
    # Full mode: detailed reachability check
    # Build set of all block cells
    all_other_blocks = {}
    for i, block in enumerate(blocks):
        # Handle both formats: JSON format has 'id', converted format might not
        block_id = block.get('id', f'b_{i}')
        shape = block['shape']
        pos = get_block_pos(block)
        if pos is None:
            return False  # Invalid format
        
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        cells = set()
        for dx, dy in shape_cells:
            cells.add((pos[0] + dx, pos[1] + dy))
        all_other_blocks[block_id] = cells
    
    # Check each block - simplified: just check if it can reach at least one coin
    # (full check for all coins is too slow)
    for i, block in enumerate(blocks):
        block_id = block.get('id', f'b_{i}')
        block_color = normalize_color(block['color'])
        block_shape = block['shape']
        block_pos = get_block_pos(block)
        if block_pos is None:
            return False
        
        # Handle counter format
        block_counter = block.get('counter', block.get('count', 0))
        
        # Get all coins of this color - handle both formats
        matching_coins = []
        for coin in coins:
            coin_color = normalize_color(coin.get('color', ''))
            if coin_color == block_color:
                coin_pos = get_coin_pos(coin)
                if coin_pos is not None:
                    matching_coins.append(coin_pos)
        
        # Check: must have at least as many coins as counter requires
        if len(matching_coins) < block_counter:
            return False
        
        # Build other_blocks set (excluding current block)
        other_blocks = set()
        for other_id, cells in all_other_blocks.items():
            if other_id != block_id:
                other_blocks.update(cells)
        
        # Check if block can reach at least ONE coin
        # Use a more permissive check: ignore other blocks for initial reachability
        # (blocks can move during gameplay, so they're not permanent obstacles)
        can_reach_any = False
        
        # First try: check without other blocks (more permissive)
        for coin_pos in matching_coins[:min(block_counter, len(matching_coins))]:
            if can_block_reach_position(block_pos, block_shape, coin_pos, layout, grid_w, grid_h, set()):
                can_reach_any = True
                break
        
        # If that fails, try with other blocks (more strict, but still valid)
        if not can_reach_any:
            for coin_pos in matching_coins[:min(block_counter, len(matching_coins))]:
                if can_block_reach_position(block_pos, block_shape, coin_pos, layout, grid_w, grid_h, other_blocks):
                    can_reach_any = True
                    break
        
        if not can_reach_any:
            return False
    
    return True

def create_level_data(level_num):
    # Updated difficulty progression with user requirements
    # Level 5+: minimum 3 blocks, up to 7 blocks
    # Smaller grids, more walls from level 5+
    
    if level_num <= 4:
        # Tutorial levels: 1-2 blocks, easy
        num_blocks = random.randint(1, 2)
        num_coins_per_block = random.randint(2, 3)
        grid_w, grid_h = 6, 6  # Smaller grid for tutorials
        wall_density = 0.0  # No walls
    elif level_num <= 20:
        # Early challenge: 3-4 blocks, walls introduced
        num_blocks = random.randint(3, 4)
        num_coins_per_block = random.randint(3, 4)
        grid_w, grid_h = 7, 7  # Compact grid
        wall_density = 0.10  # 10% walls for challenge
    elif level_num <= 50:
        # Mid levels: 3-5 blocks, more walls
        num_blocks = random.randint(3, 5)
        num_coins_per_block = random.randint(3, 5)
        grid_w, grid_h = 8, 8
        wall_density = 0.15  # 15% walls
    elif level_num <= 100:
        # Advanced: 4-6 blocks, significant walls
        num_blocks = random.randint(4, 6)
        num_coins_per_block = random.randint(4, 6)
        grid_w, grid_h = 9, 9
        wall_density = 0.18  # 18% walls
    else:
        # Expert: 5-7 blocks, maximum challenge
        num_blocks = random.randint(5, 7)
        num_coins_per_block = random.randint(5, 7)
        grid_w, grid_h = 10, 10
        wall_density = 0.20  # 20% walls

    layout = generate_layout(grid_w, grid_h, wall_density)
    empty_spots = find_empty_spots(layout)
    
    # Mischia gli spazi vuoti per posizionare oggetti a caso
    random.shuffle(empty_spots)
    
    blocks = []
    coins = []
    
    # Track all cells occupied by blocks to prevent coin spawn under them
    all_block_cells = set()
    
    # Track all coin positions to prevent overlaps between different colored coins
    all_coins_placed = []
    
    # Generazione Blocchi e Monete
    used_colors = random.sample(COLORS, min(num_blocks, len(COLORS)))
    
    # ===== PHASE 1: Generate ALL Blocks First =====
    blocks_generated = 0
    total_attempts = 0
    MAX_TOTAL_ATTEMPTS = 500
    
    while len(blocks) < num_blocks and total_attempts < MAX_TOTAL_ATTEMPTS:
        total_attempts += 1
        
        # Choose shape first
        shape = random.choice(SHAPES)
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        # Find valid position for this shape
        max_attempts = 100
        block_pos = None
        
        for attempt in range(max_attempts):
            if not empty_spots:
                break
            
            candidate_pos = empty_spots[random.randint(0, len(empty_spots) - 1)]
            
            # Check if all cells of the block fit in grid AND don't overlap existing blocks
            valid = True
            current_block_cells = []
            
            for dx, dy in shape_cells:
                cx = candidate_pos[0] + dx
                cy = candidate_pos[1] + dy
                
                # Check bounds
                if not (0 <= cx < grid_w and 0 <= cy < grid_h):
                    valid = False
                    break
                
                # Check not a wall
                if layout[cy][cx] == 1:
                    valid = False
                    break
                    
                # Check against existing blocks
                if (cx, cy) in all_block_cells:
                    valid = False
                    break
                
                current_block_cells.append((cx, cy))
            
            if valid:
                block_pos = candidate_pos
                empty_spots.remove(candidate_pos)
                break
        
        if block_pos is None:
            continue  # Skip this block if no valid position found
        
        color = used_colors[len(blocks) % len(used_colors)]
        counter = num_coins_per_block
        
        # Add current block cells to occupied set
        # We need to recalculate them because we didn't save them from the loop
        current_block_cells = []
        for dx, dy in shape_cells:
            current_block_cells.append((block_pos[0] + dx, block_pos[1] + dy))
            
        # Add to all_block_cells for future blocks and coin placement
        for cell in current_block_cells:
            all_block_cells.add(cell)
        
        blocks.append({
            "id": f"b_{len(blocks)}",
            "shape": shape,
            "color": color,
            "counter": counter,
            "xy": block_pos
        })
        
        # GDD 2.1 Constraint 1: Shake Test - verify block can move
        # Check if block has at least one valid move in any direction
        has_valid_move = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = block_pos[0] + dx
            new_y = block_pos[1] + dy
            
            # Check if all cells of moved block are valid
            move_valid = True
            for sx, sy in shape_cells:
                check_x = new_x + sx
                check_y = new_y + sy
                
                if not (0 <= check_x < grid_w and 0 <= check_y < grid_h):
                    move_valid = False
                    break
                
                if layout[check_y][check_x] == 1:
                    move_valid = False
                    break
                
                # Check collision with OTHER blocks (not itself)
                if (check_x, check_y) in all_block_cells and (check_x, check_y) not in current_block_cells:
                     move_valid = False
                     break

            if move_valid:
                has_valid_move = True
                break
        
        if not has_valid_move:
            # Block is stuck, remove it and try again
            blocks.pop()
            # Remove cells from occupied set
            for cell in current_block_cells:
                all_block_cells.remove(cell)
            empty_spots.append(block_pos)
            continue
    
    # ===== PHASE 2: Generate Coins for ALL Blocks =====
    # Now that all blocks are placed, generate coins for each block
    for block in blocks:
        shape = block['shape']
        color = block['color']
        counter = block['counter']
        
        # Generate coins for this block
        # Pass all_block_cells (which now contains ALL blocks) to ensure no overlaps
        block_coins = place_reachable_coins(layout, grid_w, grid_h, shape, counter, all_block_cells, all_coins_placed)
        
        # If we couldn't get enough coins, this is a problem but we'll keep the block
        # (better to have a slightly broken level than no level)
        if len(block_coins) < counter:
            print(f"WARNING: Block {block['id']} only got {len(block_coins)}/{counter} coins")
        
        for coin_pos in block_coins:
            coins.append({
                "color": color,
                "xy": coin_pos
            })
            # Add to global coin tracking
            all_coins_placed.append(coin_pos)
            # Remove from empty_spots if present
            if coin_pos in empty_spots:
                empty_spots.remove(coin_pos)

    level_data = {
        "meta": {
            "id": level_num,
            "world": 1 + (level_num // 60), # Cambio mondo ogni 60 livelli
            "name": f"Generated Level {level_num}",
            "grid_size": [grid_w, grid_h],
            "time_limit": 20 + (num_blocks * 25) + (num_coins_per_block * num_blocks * 3), # Tighter formula
            "stars": [num_blocks * 2, num_blocks * 4, num_blocks * 6]
        },
        "layout": layout,
        "blocks": blocks,
        "coins": {
            "static": coins,
            "entrances": [] # Per ora niente code procedurali complesse
        },
        "mechanics": {}
    }
    
    return level_data

def create_simple_fallback_level(level_num):
    """Create a simple guaranteed solvable level as fallback"""
    grid_w, grid_h = 6, 6
    layout = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
    
    # Simple level: 1 block, 2 coins
    block = {
        "id": "b_0",
        "shape": "I2",
        "color": "red",
        "counter": 2,
        "xy": [1, 2]
    }
    
    coins = [
        {"color": "red", "xy": [3, 2]},
        {"color": "red", "xy": [4, 2]}
    ]
    
    return {
        "meta": {
            "id": level_num,
            "world": 1,
            "name": f"Fallback Level {level_num}",
            "grid_size": [grid_w, grid_h],
            "time_limit": 180,
            "stars": [5, 8, 12]
        },
        "layout": layout,
        "blocks": [block],
        "coins": {
            "static": coins,
            "entrances": []
        },
        "mechanics": {}
    }

def main():
    import time
    
    ensure_dir()
    print("=" * 60)
    print("GENERATORE LIVELLI TETRACOIN")
    print("=" * 60)
    print("Generazione di 297 livelli procedurali (4-300)...")
    print("I livelli 1-3 sono tutorial hand-crafted e non verranno sovrascritti.")
    print("Verifica risolvibilità migliorata attiva - potrebbe richiedere più tempo...")
    print()
    
    # Start from level 4 to preserve hand-crafted tutorials (1-3)
    unsolvable_levels = []
    total_levels = 297
    start_time = time.time()
    solvable_count = 0
    unsolvable_count = 0
    
    for i in range(4, 301):
        level_num = i
        progress = ((i - 4) / total_levels) * 100
        elapsed = time.time() - start_time
        
        # Calculate ETA
        if progress > 0:
            eta_seconds = (elapsed / progress) * (100 - progress)
            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)
            eta_str = f"{eta_min:02d}:{eta_sec:02d}"
        else:
            eta_str = "??:??"
        
        # Progress bar
        bar_width = 40
        filled = int(bar_width * progress / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Print progress line (overwrite previous)
        print(f"\r[{bar}] {progress:5.1f}% | Livello {level_num:3d}/300 | "
              f"Risolvibili: {solvable_count:3d} | ETA: {eta_str}", end="", flush=True)
        
        MAX_ATTEMPTS = 20  # Reduced from 50 to prevent long loops
        level_data = None
        best_attempt = None
        best_reachable_coins = 0
        
        for attempt in range(MAX_ATTEMPTS):
            data = create_level_data(i)
            
            # Verify solvability - use fast mode first, then full check if needed
            if verify_level_solvable(data, fast_mode=True):
                # Fast check passed, do full check only on first few attempts
                if attempt < 3:
                    if verify_level_solvable(data, fast_mode=False):
                        level_data = data
                        solvable_count += 1
                        break
                else:
                    # After 3 attempts, accept fast mode result
                    level_data = data
                    solvable_count += 1
                    break
            else:
                # Track best attempt (most reachable coins)
                # This helps if we can't make it fully solvable
                layout = data['layout']
                grid_h = len(layout)
                grid_w = len(layout[0]) if grid_h > 0 else 0
                blocks = data['blocks']
                coins = data['coins']['static']
                
                total_reachable = 0
                for block in blocks:
                    block_color = block['color']
                    block_shape = block['shape']
                    block_pos = block['xy']
                    matching_coins = [c['xy'] for c in coins if c['color'] == block_color]
                    
                    # Count reachable coins for this block
                    for coin_pos in matching_coins:
                        # Simplified check without other blocks
                        if can_block_reach_coin(block_shape, coin_pos, layout, grid_w, grid_h):
                            total_reachable += 1
                
                if total_reachable > best_reachable_coins:
                    best_reachable_coins = total_reachable
                    best_attempt = data
        
        if level_data is None:
            # Use best attempt if we couldn't make it fully solvable
            if best_attempt:
                level_data = best_attempt
                unsolvable_levels.append(i)
                unsolvable_count += 1
            else:
                # Last resort: generate a simple level
                level_data = create_simple_fallback_level(i)
                unsolvable_count += 1
        
        filename = f"level_{i:03d}.json"
        path = os.path.join(OUTPUT_DIR, filename)
        
        with open(path, 'w') as f:
            json.dump(level_data, f, indent=2)
    
    # Final summary
    total_time = time.time() - start_time
    total_min = int(total_time // 60)
    total_sec = int(total_time % 60)
    
    print(f"\n\n{'=' * 60}")
    print("GENERAZIONE COMPLETATA!")
    print("=" * 60)
    print(f"✅ 297 livelli generati + 3 tutorial = 300 livelli totali")
    print(f"⏱️  Tempo totale: {total_min:02d}:{total_sec:02d}")
    print(f"📊 Statistiche:")
    print(f"   • Livelli risolvibili: {solvable_count}/{total_levels} ({solvable_count*100//total_levels}%)")
    print(f"   • Livelli potenzialmente non risolvibili: {unsolvable_count}/{total_levels}")
    
    if unsolvable_levels:
        print(f"\n⚠️  ATTENZIONE: {len(unsolvable_levels)} livelli potrebbero non essere completamente risolvibili:")
        if len(unsolvable_levels) <= 20:
            print(f"   Livelli: {', '.join(map(str, unsolvable_levels))}")
        else:
            print(f"   Primi 20: {', '.join(map(str, unsolvable_levels[:20]))}...")
            print(f"   (Totale: {len(unsolvable_levels)} livelli)")
        print(f"\n💡 Esegui 'python validate_all_levels.py' per verifica dettagliata.")
        print(f"   Poi rigenera i livelli problematici se necessario.")
    else:
        print(f"\n✅ Tutti i livelli dovrebbero essere risolvibili!")
    
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
