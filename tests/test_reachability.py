import unittest
from data.levels import LEVEL_DATA
from grid_manager import GridManager

class TestReachability(unittest.TestCase):
    def test_coin_reachability(self):
        for level in LEVEL_DATA:
            level_id = level['id']
            grid = GridManager(level)
            
            # For each block, check if it can reach its target coins
            # This is a simplified check: assumes no other blocks exist (best case scenario)
            # If it's impossible even without other blocks, then the level is broken.
            
            for block in level['blocks']:
                start_pos = block['start_pos']
                color = block['color']
                
                # Find all coins of this color
                target_coins = [c['pos'] for c in level['coins'] if c['color'] == color]
                
                if not target_coins:
                    continue
                    
                # BFS to find reachable cells
                reachable = set()
                queue = [start_pos]
                visited = {start_pos}
                
                while queue:
                    cx, cy = queue.pop(0)
                    reachable.add((cx, cy))
                    
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = cx + dx, cy + dy
                        
                        if grid.is_valid_pos(nx, ny) and not grid.is_wall(nx, ny) and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                            
                # Check if all coins are in reachable set
                for coin_pos in target_coins:
                    self.assertTrue(
                        coin_pos in reachable,
                        f"Level {level_id}: Block {color} at {start_pos} cannot reach coin at {coin_pos}"
                    )

if __name__ == '__main__':
    unittest.main()
