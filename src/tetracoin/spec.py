"""
Tetracoin Formal Specification Module.
This module defines the core types, entities, and physics rules for the game system.
It acts as the single source of truth for the game logic.
"""
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set

class EntityType(str, Enum):
    """Enumeration of possible entity types in the grid."""
    COIN = "COIN"
    PIGGYBANK = "PIGGYBANK"
    OBSTACLE = "OBSTACLE"
    FIXED_BLOCK = "FIXED_BLOCK"
    SUPPORT = "SUPPORT"
    DEFLECTOR = "DEFLECTOR"
    GATEWAY = "GATEWAY"
    TRAP = "TRAP"
    
class ColorType(str, Enum):
    """Standard colors for game entities."""
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    PURPLE = "PURPLE"
    ORANGE = "ORANGE"
    GRAY = "GRAY"
    
class Direction(str, Enum):
    """Cardinal directions."""
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

@dataclass
class Entity:
    """Base class for all game entities."""
    id: str
    type: EntityType
    color: ColorType
    row: int
    col: int
    
    # State flags
    is_falling: bool = False
    is_collected: bool = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "color": self.color.value,
            "row": self.row,
            "col": self.col,
            "is_falling": self.is_falling,
            "is_collected": self.is_collected
        }

@dataclass
class Coin(Entity):
    """A falling coin entity."""
    type: EntityType = field(default=EntityType.COIN, init=False)

@dataclass
class PiggyBank(Entity):
    """A container that accepts coins of matching color."""
    type: EntityType = field(default=EntityType.PIGGYBANK, init=False)
    capacity: int = 5
    current_count: int = 0
    
    @property
    def is_full(self) -> bool:
        return self.current_count >= self.capacity

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "capacity": self.capacity,
            "current_count": self.current_count
        })
        return d

@dataclass
class Obstacle(Entity):
    """An obstacle that deflects falling coins."""
    type: EntityType = field(default=EntityType.OBSTACLE, init=False)

@dataclass
class FixedBlock(Entity):
    """A static block preventing movement."""
    type: EntityType = field(default=EntityType.FIXED_BLOCK, init=False)

@dataclass
class Support(Entity):
    """A platform that holds objects but doesn't block movement sideways? Or just a static platform."""
    type: EntityType = field(default=EntityType.SUPPORT, init=False)

@dataclass
class Deflector(Entity):
    """Deviates falling objects."""
    type: EntityType = field(default=EntityType.DEFLECTOR, init=False)
    direction: str = "LEFT" # LEFT, RIGHT, etc.

    def to_dict(self):
        d = super().to_dict()
        d.update({"direction": self.direction})
        return d

@dataclass
class Gateway(Entity):
    """A conditional passage."""
    type: EntityType = field(default=EntityType.GATEWAY, init=False)
    is_open: bool = False
    condition: str = "DEFAULT" # e.g. "COIN_COUNT", "SWITCH"

    def to_dict(self):
        d = super().to_dict()
        d.update({"is_open": self.is_open, "condition": self.condition})
        return d

@dataclass
class Trap(Entity):
    """Hazardous entity."""
    type: EntityType = field(default=EntityType.TRAP, init=False)
    subtype: str = "SPIKES" # SPIKES, PIT

    def to_dict(self):
        d = super().to_dict()
        d.update({"subtype": self.subtype})
        return d
@dataclass
class GridState:
    """Snapshot of the entire grid state."""
    rows: int
    cols: int
    entities: List[Entity] = field(default_factory=list)
    
    def get_entity_at(self, row: int, col: int) -> Optional[Entity]:
        for e in self.entities:
            if e.row == row and e.col == col and not e.is_collected:
                return e
        return None
        
    def is_valid_pos(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols
        
    def is_empty(self, row: int, col: int) -> bool:
        return self.is_valid_pos(row, col) and self.get_entity_at(row, col) is None

class PhysicsEngine:
    """
    Pure logic engine for updating the game state.
    Implements gravity and collision rules.
    """
    
    @staticmethod
    def update(state: GridState) -> Tuple[GridState, List[str]]:
        """
        Advance the simulation by one tick.
        Returns:
            - The new state
            - A list of events triggered (e.g. "COLLECT_RED", "LEVEL_COMPLETE")
        """
        events = []
        
        # 1. Apply Gravity (Bottom-up to avoid double processing)
        # Sort entities by row descending
        entities_by_row = sorted(state.entities, key=lambda e: e.row, reverse=True)
        
        for entity in entities_by_row:
            if entity.is_collected:
                continue
                
            if entity.type == EntityType.COIN:
                PhysicsEngine._update_coin(entity, state, events)
                
        return state, events
    
    @staticmethod
    def _update_coin(coin: Coin, state: GridState, events: List[str]):
        """Apply gravity logic to a single coin."""
        
        # Target position: directly below
        target_row = coin.row + 1
        target_col = coin.col
        
        if not state.is_valid_pos(target_row, target_col):
            # Hit bottom of grid - blocked or despawn?
            # For now, treat as blocked (stops falling)
            coin.is_falling = False
            return

        collider = state.get_entity_at(target_row, target_col)
        
        if collider is None:
            # Free fall
            coin.row = target_row
            coin.is_falling = True
            
        elif collider.type == EntityType.PIGGYBANK:
            # Check interaction with PiggyBank
            piggy: PiggyBank = collider # Type hint
            if piggy.color == coin.color and not piggy.is_full:
                # Collect!
                piggy.current_count += 1
                coin.is_collected = True
                events.append(f"COLLECT_{coin.color.value}")
                
                if piggy.is_full:
                    events.append(f"PIGGYBANK_FULL_{piggy.id}")
            else:
                # Wrong color or full -> Blocked
                coin.is_falling = False
                
        elif collider.type == EntityType.OBSTACLE or collider.type == EntityType.FIXED_BLOCK or collider.type == EntityType.COIN:
            # Hit something solid. Try to slide ("Sand Fall").
            # Check diagonals: Down-Left and Down-Right
            
            can_slide_left = state.is_empty(target_row, target_col - 1) and state.is_empty(coin.row, coin.col - 1)
            can_slide_right = state.is_empty(target_row, target_col + 1) and state.is_empty(coin.row, coin.col + 1)
            
            if can_slide_left and can_slide_right:
                # If both open, choice strategy? Random or alternated?
                # For determinism, maybe prefer left or right based on id hash, or stay put?
                # Drop Away mechanics usually have determinism.
                # Let's say: stay put if perfectly balanced? Or slide left default.
                pass 
                # For now simplify: strict gravity unless obstacle deflects
            
            if collider.type == EntityType.OBSTACLE:
                # Deflection logic (bounce)
                pass
                
            coin.is_falling = False # Stop for now if simple stack
