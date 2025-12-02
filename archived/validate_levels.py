"""
Validate generated levels to ensure all coins are reachable
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import random
from core.level_loader import LevelLoader
from core.sprites import SHAPES

def validate_level(level_data):
    """Check if all coins in a level are reachable"""
    layout = level_data['layout']
    grid_w = level_data['grid_cols']
    grid_h = level_data['grid_rows']
    
    issues = []
    
    for block_data in level_data['blocks']:
        shape_name = block_data.get('shape', 'I2')
        shape_cells = SHAPES.get(shape_name, [(0, 0)])
        block_color = block_data['color']
        
        # Find coins of this color
        matching_coins = [c for c in level_data['coins']['static'] if c['color'] == block_color]
        
        for coin in matching_coins:
            coin_pos = tuple(coin['pos'])
            reachable = False
            
            # Try all possible block positions
            for bx in range(grid_w):
                for by in range(grid_h):
                    valid = True
                    overlaps = False
                    
                    for dx, dy in shape_cells:
                        cx, cy = bx + dx, by + dy
                        
                        if not (0 <= cx < grid_w and 0 <= cy < grid_h):
                            valid = False
                            break
                        
                        if layout[cy][cx] == 1:
                            valid = False
                            break
                        
                        if (cx, cy) == coin_pos:
                            overlaps = True
                    
                    if valid and overlaps:
                        reachable = True
                        break
                
                if reachable:
                    break
            
            if not reachable:
                issues.append(f"Coin {block_color} at {coin_pos} is UNREACHABLE by {shape_name} block")
    
    return issues

# Test random sample of generated levels
loader = LevelLoader()
test_levels = [4, 10, 25, 50, 100, 150, 200, 250, 300]

print("=" * 60)
print("VALIDATING GENERATED LEVELS")
print("=" * 60)

total_issues = 0

for level_num in test_levels:
    try:
        level = loader.load_level(level_num)
        issues = validate_level(level)
        
        if issues:
            print(f"\n❌ Level {level_num}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"   - {issue}")
            total_issues += len(issues)
        else:
            print(f"✓ Level {level_num}: OK")
    except Exception as e:
        print(f"❌ Level {level_num}: ERROR - {e}")
        total_issues += 1

print("\n" + "=" * 60)
if total_issues == 0:
    print("✅ ALL TESTED LEVELS ARE VALID!")
else:
    print(f"⚠️  Found {total_issues} total issues")
print("=" * 60)
