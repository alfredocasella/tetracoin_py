import pygame
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.game import Game
from core.settings import *
from src.tetracoin.generator import TetracoinGridGenerator
from src.tetracoin.spec import GridState

def main():
    print("Initializing Pygame...")
    pygame.init()
    
    print("Generating Level...")
    # Generate a level
    gen = TetracoinGridGenerator(
        difficulty=3,
        grid_width=7,
        grid_height=9,
        num_coins=8,
        num_piggybanks=2,
        seed=None # Random
    )
    
    grid_state = gen.generate(max_attempts=50)
    
    if not grid_state:
        print("Failed to generate level!")
        return
        
    print(f"Level Generated. Coins: {len([e for e in grid_state.entities if e.type == 'COIN'])}")
    
    # Serialize to JSON format for Game loader
    # Construct level data dictionary
    # Game needs 'entities' key to trigger Physics Mode
    
    # GridState to dict
    entities_data = [e.to_dict() for e in grid_state.entities]
    
    level_data = {
        "id": "generated_test",
        "grid": {
            "cols": grid_state.cols,
            "rows": grid_state.rows
        },
        "entities": entities_data,
        "layout": [[0]*grid_state.cols for _ in range(grid_state.rows)], # Dummy layout
        "blocks": [],
        "coins": {"static": []}
    }
    
    # Save to file (optional, for inspection)
    with open("assets/examples/generated_level_test.json", "w") as f:
        json.dump(level_data, f, indent=2)
        
    print("Starting Game...")
    
    game = Game()
    
    # Inject level data
    game.level_data = level_data
    game.state = game.STATE_PLAY
    
    # Initialize Physics Level
    game._init_physics_level()
    game.mode = "PHYSICS"
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        game.update(dt)
        game.draw(game.screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
