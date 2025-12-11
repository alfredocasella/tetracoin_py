#!/usr/bin/env python3
"""
Fix rapido per ottimizzare il BFS nel level_generator_v3.py
Riduce max_states e max_moves per evitare loop infiniti
"""

import re

# Leggi il file
with open('scripts/level_generator_v3.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Ridurre max_states da 10000 a 5000
content = content.replace('max_states = 10000', 'max_states = 5000')

# Fix 2: Ridurre max_moves default da 100 a 50
content = content.replace(
    'def is_solvable(self, level_data: Dict, max_moves: int = 100)',
    'def is_solvable(self, level_data: Dict, max_moves: int = 50)'
)

# Fix 3: Aggiungere timeout per quick_validate
old_quick = '''    def quick_validate(self, level_data: Dict) -> Tuple[bool, str]:
        """Pre-validazione veloce senza solver (euristiche)"""
        
        # 1. Verifica connettività
        connectivity = self.analyzer.calculate_connectivity(level_data['layout'])
        if connectivity < 0.7:  # Almeno 70% di celle raggiungibili
            return False, f"Low connectivity: {connectivity:.2f}"'''

new_quick = '''    def quick_validate(self, level_data: Dict) -> Tuple[bool, str]:
        """Pre-validazione veloce senza solver (euristiche)"""
        
        # 1. Verifica connettività
        connectivity = self.analyzer.calculate_connectivity(level_data['layout'])
        if connectivity < 0.8:  # Aumentato a 80% per essere più restrittivi
            return False, f"Low connectivity: {connectivity:.2f}"'''

content = content.replace(old_quick, new_quick)

# Salva
with open('scripts/level_generator_v3.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Ottimizzazioni applicate:")
print("   - max_states: 10000 → 5000")
print("   - max_moves default: 100 → 50")
print("   - connectivity minima: 70% → 80%")
