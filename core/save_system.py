"""
Save System for TetraCoin
Handles player progress, stars, currency, and settings persistence
"""
import json
import os
from typing import Dict, Optional

class SaveSystem:
    def __init__(self, save_file="data/player_save.json"):
        self.save_file = save_file
        self.data = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        """Load existing save or create new one"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading save file: {e}")
                return self._create_new_save()
        else:
            return self._create_new_save()
    
    def _create_new_save(self) -> Dict:
        """Create a new save file with default values"""
        return {
            "player": {
                "name": "Player",
                "total_stars": 0,
                "tetra_gold": 0,
                "current_world": 1,
                "unlocked_levels": 1,
                "total_moves": 0,
                "total_time_played": 0
            },
            "levels": {},
            "settings": {
                "music_volume": 0.7,
                "sfx_volume": 0.8,
                "language": "en"
            },
            "power_ups": {
                "hammer": 0,
                "magnet": 0,
                "time_freeze": 0
            }
        }
    
    def save(self):
        """Write current data to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            with open(self.save_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def complete_level(self, level_id, stars: int, moves: int, time: float):
        """Record level completion"""
        # Convert level_id to int if it's a string like 'level_001'
        if isinstance(level_id, str):
            # Extract number from string like 'level_001' or use as-is if already numeric string
            if level_id.startswith('level_'):
                level_num = int(level_id.split('_')[1])
            else:
                try:
                    level_num = int(level_id)
                except ValueError:
                    level_num = 1  # Default fallback
        else:
            level_num = level_id
        
        level_key = str(level_num)
        
        # Get existing level data or create new
        if level_key not in self.data["levels"]:
            self.data["levels"][level_key] = {
                "completed": False,
                "stars": 0,
                "best_moves": 999999,
                "best_time": 999999,
                "attempts": 0
            }
        
        level_data = self.data["levels"][level_key]
        level_data["attempts"] += 1
        level_data["completed"] = True
        
        # Update best scores
        if stars > level_data["stars"]:
            level_data["stars"] = stars
            # Award gold for new stars
            stars_gained = stars - level_data.get("previous_stars", 0)
            self.add_gold(stars_gained * 5)
        
        if moves < level_data["best_moves"]:
            level_data["best_moves"] = moves
        
        if time < level_data["best_time"]:
            level_data["best_time"] = time
        
        # Award gold for completion (if first time)
        if level_data["attempts"] == 1:
            self.add_gold(10)
        
        # Update player stats
        self.data["player"]["total_stars"] = sum(
            lvl.get("stars", 0) for lvl in self.data["levels"].values()
        )
        self.data["player"]["total_moves"] += moves
        self.data["player"]["total_time_played"] += time
        
        # Unlock next level
        if level_num >= self.data["player"]["unlocked_levels"]:
            self.data["player"]["unlocked_levels"] = level_num + 1
        
        self.save()
    
    def get_level_data(self, level_id: int) -> Optional[Dict]:
        """Get data for a specific level"""
        return self.data["levels"].get(str(level_id))
    
    def is_level_unlocked(self, level_id: int) -> bool:
        """Check if level is unlocked"""
        return level_id <= self.data["player"]["unlocked_levels"]
    
    def add_gold(self, amount: int):
        """Add TetraGold to player"""
        self.data["player"]["tetra_gold"] += amount
        self.save()
    
    def spend_gold(self, amount: int) -> bool:
        """Spend TetraGold if player has enough"""
        if self.data["player"]["tetra_gold"] >= amount:
            self.data["player"]["tetra_gold"] -= amount
            self.save()
            return True
        return False
    
    def get_gold(self) -> int:
        """Get current gold amount"""
        return self.data["player"]["tetra_gold"]
    
    def get_total_stars(self) -> int:
        """Get total stars earned"""
        return self.data["player"]["total_stars"]
    
    def buy_power_up(self, power_up_name: str, cost: int) -> bool:
        """Purchase a power-up"""
        if self.spend_gold(cost):
            self.data["power_ups"][power_up_name] = self.data["power_ups"].get(power_up_name, 0) + 1
            self.save()
            return True
        return False
    
    def use_power_up(self, power_up_name: str) -> bool:
        """Use a power-up if available"""
        if self.data["power_ups"].get(power_up_name, 0) > 0:
            self.data["power_ups"][power_up_name] -= 1
            self.save()
            return True
        return False
    
    def get_power_up_count(self, power_up_name: str) -> int:
        """Get count of a specific power-up"""
        return self.data["power_ups"].get(power_up_name, 0)
    
    def reset_progress(self):
        """Reset all progress (for testing or new game)"""
        self.data = self._create_new_save()
        self.save()
