import unittest
from data.levels import LEVEL_DATA

class TestLevelDesign(unittest.TestCase):
    def test_block_coin_counts(self):
        for level in LEVEL_DATA:
            level_id = level['id']
            
            # Count required coins per color based on blocks
            required_coins = {}
            for block in level['blocks']:
                color = block['color']
                count = block['count']
                required_coins[color] = required_coins.get(color, 0) + count
            
            # Count available coins per color
            available_coins = {}
            for coin in level['coins']:
                color = coin['color']
                available_coins[color] = available_coins.get(color, 0) + 1
            
            # Verify match
            for color, count in required_coins.items():
                self.assertEqual(
                    count, 
                    available_coins.get(color, 0), 
                    f"Level {level_id}: Block requires {count} {color} coins, but found {available_coins.get(color, 0)}"
                )

if __name__ == '__main__':
    unittest.main()
