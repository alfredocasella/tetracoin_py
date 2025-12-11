#!/usr/bin/env python3
"""
Fix per usare solver esterno (veloce) invece di BFS integrato (lento)
Mantiene le euristiche intelligenti del V3
"""

# Leggi il file
with open('scripts/level_generator_v3.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Sostituisci validate_level per usare solver esterno
old_validate = '''    def validate_level(self, level_data: Dict, min_moves: int = 5) -> Tuple[bool, str, int]:
        """Validazione completa con BFS integrato"""
        
        # Prima: validazione rapida
        quick_ok, quick_msg = self.quick_validate(level_data)
        if not quick_ok:
            return False, f"Quick check failed: {quick_msg}", 0
        
        # Poi: validazione strutturale
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # Infine: BFS solver integrato (costoso)
        is_solvable, num_moves = self.is_solvable(level_data)
        
        if not is_solvable:
            return False, "Level is not solvable", 0
        
        if num_moves < min_moves:
            return False, f"Too easy: only {num_moves} moves", num_moves
        
        return True, "Valid", num_moves'''

new_validate = '''    def validate_level(self, level_data: Dict, min_moves: int = 5) -> Tuple[bool, str, int]:
        """Validazione completa con solver esterno (VELOCE)"""
        
        # Prima: validazione rapida (euristiche)
        quick_ok, quick_msg = self.quick_validate(level_data)
        if not quick_ok:
            return False, f"Quick check failed: {quick_msg}", 0
        
        # Poi: validazione strutturale
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # Infine: solver esterno (MOLTO PIÙ VELOCE del BFS integrato)
        max_moves = level_data['meta'].get('stars', [0, 0, 100])[2] + 20
        
        if SOLVER_AVAILABLE:
            # Usa solver esterno ottimizzato
            is_solvable, solution, num_moves = solve_level(level_data, max_moves=max_moves, verbose=False)
        else:
            # Fallback a BFS integrato (lento)
            is_solvable, num_moves = self.is_solvable(level_data, max_moves=max_moves)
        
        if not is_solvable:
            return False, "Level is not solvable", 0
        
        if num_moves < min_moves:
            return False, f"Too easy: only {num_moves} moves", num_moves
        
        return True, "Valid", num_moves'''

content = content.replace(old_validate, new_validate)

# Salva
with open('scripts/level_generator_v3.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ V3 Ibrido creato!")
print("   ✓ Euristiche intelligenti V3 (layout, zone, monete)")
print("   ✓ Solver esterno veloce per validazione")
print("   ✓ Fallback a BFS integrato se solver non disponibile")
print()
print("Ora puoi generare livelli difficili velocemente!")
