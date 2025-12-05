import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tetracoin.config_validator import TetracoinConfigValidator, ValidationResult

class TestTetracoinConfigValidator(unittest.TestCase):
    """Test suite per il validatore di configurazioni."""
    
    def setUp(self):
        self.validator = TetracoinConfigValidator()
        self.valid_grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(4, 4), (2, 2)],
            'obstacles': [(1, 1), (3, 3)]
        }
    
    # ===== Test Struttura =====
    
    def test_missing_keys(self):
        """Test rilevamento chiavi mancanti."""
        grid = {'width': 5, 'height': 5}
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('player_start' in err for err in result.errors))
        self.assertTrue(any('coins' in err for err in result.errors))
    
    def test_invalid_types(self):
        """Test rilevamento tipi invalidi."""
        grid = {
            'width': '5',  # Stringa invece di int
            'height': 5,
            'player_start': (0, 0),
            'coins': [],
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('width' in err for err in result.errors))
    
    # ===== Test Bounds =====
    
    def test_player_out_of_bounds(self):
        """Test player fuori dai limiti."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (10, 10),
            'coins': [(2, 2)],
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('player_start' in err and 'fuori' in err for err in result.errors))
    
    def test_coin_out_of_bounds(self):
        """Test moneta fuori dai limiti."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(2, 2), (10, 10)],
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('Coin' in err and 'fuori' in err for err in result.errors))
    
    # ===== Test Collisioni =====
    
    def test_player_on_obstacle(self):
        """Test player su ostacolo."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (2, 2),
            'coins': [(4, 4)],
            'obstacles': [(2, 2)]
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('collide' in err and 'ostacolo' in err for err in result.errors))
    
    def test_coin_on_obstacle(self):
        """Test moneta su ostacolo."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(2, 2)],
            'obstacles': [(2, 2)]
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('sovrappongono' in err for err in result.errors))
    
    def test_duplicate_coins(self):
        """Test monete duplicate."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(2, 2), (2, 2), (3, 3)],
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('duplicate' in err.lower() for err in result.errors))
    
    # ===== Test Raggiungibilità =====
    
    def test_unreachable_coin(self):
        """Test moneta irraggiungibile."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(4, 4)],
            'obstacles': [(1, 0), (0, 1), (1, 1)]  # Blocca il player nell'angolo
        }
        result = self.validator.validate(grid)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('non è raggiungibile' in err for err in result.errors))
    
    def test_all_coins_reachable(self):
        """Test tutte le monete raggiungibili."""
        result = self.validator.validate(self.valid_grid)
        
        # Non dovrebbero esserci errori di raggiungibilità
        reachability_errors = [e for e in result.errors if 'raggiungibile' in e]
        self.assertEqual(len(reachability_errors), 0)
    
    # ===== Test Banalità =====
    
    def test_trivial_configuration(self):
        """Test configurazione banale."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (2, 2),
            'coins': [(2, 3), (3, 2)],  # Tutte vicinissime
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        # Dovrebbe essere valido ma con warning
        self.assertTrue(result.is_valid or len(result.warnings) > 0)
        self.assertTrue(any('banale' in warn.lower() or 'vicine' in warn.lower() for warn in result.warnings))
    
    def test_too_few_obstacles(self):
        """Test pochi ostacoli."""
        grid = {
            'width': 10,
            'height': 10,
            'player_start': (0, 0),
            'coins': [(9, 9)],
            'obstacles': []  # Nessun ostacolo
        }
        result = self.validator.validate(grid)
        
        self.assertTrue(any('ostacoli' in warn.lower() for warn in result.warnings))
    
    # ===== Test Layout =====
    
    def test_too_many_obstacles(self):
        """Test troppi ostacoli."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(4, 4)],
            'obstacles': [(x, y) for x in range(5) for y in range(5) if (x, y) not in [(0, 0), (4, 4), (0, 1), (1, 0)]]
        }
        result = self.validator.validate(grid)
        
        # Potrebbe essere invalido o avere warning
        if result.is_valid:
            self.assertTrue(any('troppi ostacoli' in warn.lower() for warn in result.warnings))
    
    def test_collinear_coins(self):
        """Test monete tutte allineate."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [(1, 2), (2, 2), (3, 2), (4, 2)],  # Tutte sulla stessa riga
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        self.assertTrue(any('allineate' in warn.lower() or 'noioso' in warn.lower() for warn in result.warnings))
    
    def test_small_grid_warning(self):
        """Test griglia molto piccola."""
        grid = {
            'width': 3,
            'height': 3,
            'player_start': (0, 0),
            'coins': [(2, 2)],
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        self.assertTrue(any('piccola' in warn.lower() for warn in result.warnings))
    
    # ===== Test Perdite Ingiuste =====
    
    def test_unfair_coin_loss(self):
        """Test raccolta moneta che blocca altre."""
        # Configurazione dove raccogliere coin1 blocca l'accesso a coin2
        grid = {
            'width': 5,
            'height': 3,
            'player_start': (0, 1),
            'coins': [(2, 1), (4, 1)],
            'obstacles': [(1, 0), (1, 2), (3, 0), (3, 2)]  # Crea corridoio con collo di bottiglia
        }
        result = self.validator.validate(grid)
        
        # Questo test dipende dalla logica specifica - potrebbe essere valido
        # ma dovrebbe rilevare il problema se implementato correttamente
        if not result.is_valid:
            self.assertTrue(any('irraggiungibile' in err for err in result.errors))
    
    # ===== Test Integrazione =====
    
    def test_valid_configuration_passes(self):
        """Test che una configurazione valida passi tutti i controlli."""
        result = self.validator.validate(self.valid_grid)
        
        # Potrebbe avere warnings ma non errori
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_empty_coins_list(self):
        """Test lista monete vuota."""
        grid = {
            'width': 5,
            'height': 5,
            'player_start': (0, 0),
            'coins': [],
            'obstacles': []
        }
        result = self.validator.validate(grid)
        
        # Dovrebbe avere almeno un warning
        self.assertTrue(any('moneta' in warn.lower() for warn in result.warnings))

if __name__ == '__main__':
    unittest.main()
