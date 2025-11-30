#!/usr/bin/env python3
"""
Complete Level Solver - Simulates actual gameplay to verify solvability
Uses BFS to explore all possible game states and find winning sequences
"""

from collections import deque
from typing import Dict, Set, Tuple, List, Optional
import json

# Import shape definitions from level_generator
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from level_generator import SHAPE_CELLS


class GameState:
    """Represents a complete game state"""
    
    def __init__(self, level_data):
        """Initialize from level data"""
        self.layout = level_data['layout']
        self.grid_h = len(self.layout)
        self.grid_w = len(self.layout[0]) if self.grid_h > 0 else 0
        
        # Blocks: {block_id: {'pos': (x,y), 'shape': str, 'color': str, 'counter': int}}
        self.blocks = {}
        for block in level_data['blocks']:
            self.blocks[block['id']] = {
                'pos': tuple(block['xy']),
                'shape': block['shape'],
                'color': block['color'],
                'counter': block['counter']
            }
        
        # Coins: set of (x, y, color)
        self.coins = set()
        for coin in level_data['coins']['static']:
            self.coins.add((coin['xy'][0], coin['xy'][1], coin['color']))
        
        # Collected coins per color
        self.collected = {}
        for block in self.blocks.values():
            self.collected[block['color']] = 0
    
    def copy(self):
        """Create a deep copy of this state"""
        new_state = GameState.__new__(GameState)
        new_state.layout = self.layout  # Layout is immutable
        new_state.grid_h = self.grid_h
        new_state.grid_w = self.grid_w
        new_state.blocks = {bid: bdata.copy() for bid, bdata in self.blocks.items()}
        new_state.coins = self.coins.copy()
        new_state.collected = self.collected.copy()
        return new_state
    
    def to_hash(self):
        """Create hashable representation for visited set"""
        # Hash: block positions + remaining coins
        block_positions = tuple(sorted((bid, bdata['pos']) for bid, bdata in self.blocks.items()))
        remaining_coins = tuple(sorted(self.coins))
        return (block_positions, remaining_coins)
    
    def is_win(self):
        """Check if all required coins are collected"""
        for block_id, block_data in self.blocks.items():
            color = block_data['color']
            required = block_data['counter']
            collected = self.collected.get(color, 0)
            if collected < required:
                return False
        return True
    
    def get_block_cells(self, block_id):
        """Get all cells occupied by a block"""
        block = self.blocks[block_id]
        pos = block['pos']
        shape = block['shape']
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        cells = set()
        for dx, dy in shape_cells:
            cells.add((pos[0] + dx, pos[1] + dy))
        return cells
    
    def is_valid_position(self, block_id, new_pos):
        """Check if a block can be at a position"""
        block = self.blocks[block_id]
        shape = block['shape']
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        # Get all other block cells
        other_cells = set()
        for other_id in self.blocks:
            if other_id != block_id:
                other_cells.update(self.get_block_cells(other_id))
        
        # Check each cell of the block
        for dx, dy in shape_cells:
            cell_x = new_pos[0] + dx
            cell_y = new_pos[1] + dy
            
            # Check bounds
            if not (0 <= cell_x < self.grid_w and 0 <= cell_y < self.grid_h):
                return False
            
            # Check walls
            if self.layout[cell_y][cell_x] == 1:
                return False
            
            # Check collision with other blocks
            if (cell_x, cell_y) in other_cells:
                return False
            
            # Check collision with coins (coins are obstacles!)
            # Exception: coins of the same color as the block are NOT obstacles
            for coin_x, coin_y, coin_color in self.coins:
                if (cell_x, cell_y) == (coin_x, coin_y):
                    if coin_color != block['color']:
                        return False  # Coin of different color blocks movement
        
        return True
    
    def try_move(self, block_id, direction):
        """
        Try to move a block in a direction
        Returns: new GameState or None if invalid
        """
        dx, dy = direction
        block = self.blocks[block_id]
        old_pos = block['pos']
        new_pos = (old_pos[0] + dx, old_pos[1] + dy)
        
        # Check if move is valid
        if not self.is_valid_position(block_id, new_pos):
            return None
        
        # Create new state
        new_state = self.copy()
        new_state.blocks[block_id]['pos'] = new_pos
        
        # Check for coin collection
        block_color = block['color']
        new_cells = set()
        shape_cells = SHAPE_CELLS.get(block['shape'], [(0, 0)])
        for dx2, dy2 in shape_cells:
            new_cells.add((new_pos[0] + dx2, new_pos[1] + dy2))
        
        # Collect coins
        coins_to_remove = set()
        for coin_x, coin_y, coin_color in new_state.coins:
            if (coin_x, coin_y) in new_cells and coin_color == block_color:
                coins_to_remove.add((coin_x, coin_y, coin_color))
                new_state.collected[block_color] += 1
        
        new_state.coins -= coins_to_remove
        
        return new_state
    
    def get_possible_moves(self):
        """Generate all possible moves from this state"""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # down, up, right, left
        direction_names = ['down', 'up', 'right', 'left']
        
        for block_id in self.blocks:
            for direction, dir_name in zip(directions, direction_names):
                new_state = self.try_move(block_id, direction)
                if new_state is not None:
                    moves.append((block_id, dir_name, new_state))
        
        return moves


def solve_level(level_data, max_moves=50, verbose=False):
    """
    Solve a level using BFS
    Returns: (is_solvable, solution_moves, num_moves)
    """
    initial_state = GameState(level_data)
    
    # Check if already won (shouldn't happen but just in case)
    if initial_state.is_win():
        return True, [], 0
    
    queue = deque([(initial_state, [])])
    visited = set()
    visited.add(initial_state.to_hash())
    
    states_explored = 0
    max_states = 10000  # Prevent infinite loops
    
    while queue and states_explored < max_states:
        state, moves = queue.popleft()
        states_explored += 1
        
        # Try all possible moves
        for block_id, direction, new_state in state.get_possible_moves():
            # Check if we've seen this state
            state_hash = new_state.to_hash()
            if state_hash in visited:
                continue
            visited.add(state_hash)
            
            new_moves = moves + [(block_id, direction)]
            
            # Check if too many moves
            if len(new_moves) > max_moves:
                continue
            
            # Check win condition
            if new_state.is_win():
                if verbose:
                    print(f"✅ Solution found in {len(new_moves)} moves (explored {states_explored} states)")
                return True, new_moves, len(new_moves)
            
            queue.append((new_state, new_moves))
    
    if verbose:
        print(f"❌ No solution found (explored {states_explored} states, visited {len(visited)} unique states)")
    
    return False, [], 0


def test_solver():
    """Test the solver with a simple level"""
    # Simple test level: 1 block, 2 coins
    test_level = {
        "layout": [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ],
        "blocks": [
            {
                "id": "b_0",
                "shape": "I2",
                "color": "red",
                "counter": 2,
                "xy": [1, 1]
            }
        ],
        "coins": {
            "static": [
                {"color": "red", "xy": [3, 1]},
                {"color": "red", "xy": [3, 3]}
            ],
            "entrances": []
        }
    }
    
    print("Testing solver with simple level...")
    is_solvable, solution, num_moves = solve_level(test_level, verbose=True)
    
    if is_solvable:
        print(f"\n✅ Level is solvable!")
        print(f"Solution ({num_moves} moves):")
        for i, (block_id, direction) in enumerate(solution, 1):
            print(f"  {i}. Move {block_id} {direction}")
    else:
        print("\n❌ Level is NOT solvable")
    
    return is_solvable


if __name__ == "__main__":
    test_solver()
