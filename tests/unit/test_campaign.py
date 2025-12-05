import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from unittest.mock import MagicMock
from src.tetracoin.campaign import TetracoinCampaignProgressionGenerator, CampaignLevel
from src.tetracoin.level_generator import TetracoinLevelGenerator
from src.tetracoin.difficulty import TetracoinDifficultyAnalyzer, DifficultyReport, DifficultyTier
from src.tetracoin.spec import GridState
from src.tetracoin.level_generator_spec import TetracoinLevel

class TestCampaignGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_level_gen = MagicMock(spec=TetracoinLevelGenerator)
        self.mock_diff_analyzer = MagicMock(spec=TetracoinDifficultyAnalyzer)
        
        # Setup mocks
        self.mock_level_gen.grid_generator = MagicMock()
        self.mock_level_gen.grid_generator.to_config_dict.return_value = {}
        
        # Mock generate return
        mock_level = TetracoinLevel(
            id="MOCK_ID",
            grid=GridState(rows=5, cols=5),
            config=MagicMock(),
            metadata=MagicMock(),
            solution_hint=[]
        )
        self.mock_level_gen.generate.return_value = mock_level
        
        # Mock analyze return
        self.mock_diff_analyzer.analyze.return_value = DifficultyReport(
            score=50.0,
            tier=DifficultyTier.MEDIUM,
            metrics=MagicMock(),
            breakdown={}
        )
        
        self.generator = TetracoinCampaignProgressionGenerator(
            level_generator=self.mock_level_gen,
            difficulty_analyzer=self.mock_diff_analyzer,
            boss_level_interval=5
        )

    def test_campaign_length(self):
        """Test correct number of levels generated."""
        campaign = self.generator.generate_campaign(num_levels=10, tutorial_levels=2)
        self.assertEqual(len(campaign), 10)
        self.assertEqual(len([c for c in campaign if c.is_tutorial]), 2)

    def test_boss_placement(self):
        """Test boss levels are placed correctly."""
        # 10 levels, 2 tut. 8 main.
        # Main indices: 1..8. Boss interval 5.
        # Boss should be at main index 5 => Absolute index 2+5 = 7?
        # Let's check logic: abs_index starts at start_index + 1 => 3.
        # Loop i=0..7.
        # i=4 => abs_index = 3+4 = 7. Not div by 5.
        # Logic was: abs_index % boss_interval == 0.
        # So boss at 5, 10.
        # Tutorial take 1, 2.
        # Campaign starts at 3.
        # Level 5 is in campaign. Level 10 is in campaign.
        
        campaign = self.generator.generate_campaign(num_levels=10, tutorial_levels=2)
        
        # Level 5 (index 4) should be boss
        self.assertTrue(campaign[4].is_boss, f"Level 5 should be boss. ID: {campaign[4].level_id}")
        self.assertTrue(campaign[9].is_boss, f"Level 10 should be boss. ID: {campaign[9].level_id}")

    def test_tutorial_config(self):
        """Verify tutorial calls use custom config logic via mock calls if possible."""
        # This is harder to verify without inspecting call args deeply, 
        # but we can check if is_tutorial flag is set.
        campaign = self.generator.generate_campaign(num_levels=5, tutorial_levels=2)
        self.assertTrue(campaign[0].is_tutorial)
        self.assertTrue(campaign[1].is_tutorial)
        self.assertFalse(campaign[2].is_tutorial)

if __name__ == '__main__':
    unittest.main()
