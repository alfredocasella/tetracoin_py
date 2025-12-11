import json
import os
from typing import Dict, List

class LevelLoader:
    """Loads levels from JSON files"""
    
    def __init__(self, levels_dir="data/levels"):  # Using stable legacy levels
        self.levels_dir = levels_dir
        self.levels_cache = {}
        self.level_count = 0
        self._scan_levels()
    
    def _scan_levels(self):
        """Scan the levels directory and count available levels"""
        if not os.path.exists(self.levels_dir):
            print(f"Warning: Levels directory '{self.levels_dir}' not found")
            return
        
        json_files = [f for f in os.listdir(self.levels_dir) if f.endswith('.json') and f != 'index.json']
        self.level_count = len(json_files)
        print(f"Found {self.level_count} level files")
    
    def load_level(self, level_num: int) -> Dict:
        """Load a specific level by number (1-indexed)"""
        # Check cache first
        if level_num in self.levels_cache:
            return self.levels_cache[level_num]
        
        # Construct filename
        filename = f"level_{level_num:03d}.json"
        filepath = os.path.join(self.levels_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Level file not found: {filepath}")
        
        # Load JSON
        with open(filepath, 'r') as f:
            level_data = json.load(f)
        
        # Check if this is v2 format (has 'grid' and 'entities' keys)
        if 'grid' in level_data and 'entities' in level_data:
            # V2 format - use directly, no conversion needed
            converted = level_data
        else:
            # Legacy format - convert
            converted = self._convert_format(level_data)
        
        # Cache it
        self.levels_cache[level_num] = converted
        
        return converted
    
    def _convert_format(self, json_data: Dict) -> Dict:
        """Convert old JSON format to the format expected by the game"""
        meta = json_data.get('meta', {})
        grid_size = meta.get('grid_size', [6, 6])
        
        # Convert blocks format
        blocks = []
        for block in json_data.get('blocks', []):
            blocks.append({
                'shape': block['shape'],
                'color': block['color'].upper(),  # Convert to uppercase for consistency
                'count': block['counter'],
                'start_pos': tuple(block['xy'])
            })
        
        # Convert coins format
        coins_data = json_data.get('coins', {})
        static_coins = []
        for coin in coins_data.get('static', []):
            static_coins.append({
                'color': coin['color'].upper(),
                'pos': tuple(coin['xy'])
            })
        
        # Convert coin queues - check both 'queues' and 'entrances' keys
        queues = []
        # First try 'queues' (new format)
        for queue_data in coins_data.get('queues', []):
            queues.append({
                'pos': tuple(queue_data['pos']),
                'items': [c.upper() for c in queue_data['items']]
            })
        # Then try 'entrances' (old format)
        for entrance in coins_data.get('entrances', []):
            queues.append({
                'pos': tuple(entrance['xy']),
                'items': [c.upper() for c in entrance['queue']]
            })
        
        # Build final format - INCLUDE META!
        converted = {
            'meta': meta,  # CRITICAL: Include full meta object
            'id': meta.get('id', 1),
            'grid_cols': grid_size[0],
            'grid_rows': grid_size[1],
            'layout': json_data.get('layout', []),
            'blocks': blocks,
            'coins': {
                'static': static_coins,
                'queues': queues
            },
            'stars_thresholds': meta.get('stars', [10, 15, 20])
        }
        
        return converted
    
    def get_level_count(self) -> int:
        """Return total number of available levels"""
        return self.level_count
