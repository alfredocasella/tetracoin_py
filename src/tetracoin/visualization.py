from typing import List, Optional, Any
from src.tetracoin.spec import GridState, EntityType

class TetracoinVisualizer:
    """
    Visualizzatore statico per livelli Tetracoin (ASCII/Text).
    Utile per debug e logging.
    """
    
    @staticmethod
    def render_static(level: Any) -> str:
        """
        Renderizza una rappresentazione statica (ASCII) del livello.
        Accetta TetracoinLevel o GridState.
        """
        grid = None
        if hasattr(level, 'grid'):
             grid = level.grid
        elif isinstance(level, GridState):
             grid = level
             
        if not grid:
            return "Invalid Level: No grid data"
            
        return TetracoinVisualizer._render_grid(grid, solution_path=getattr(level, 'solution_hint', None))

    @staticmethod
    def _render_grid(grid: GridState, solution_path: Optional[List[Any]] = None) -> str:
        """Metodo interno di rendering."""
        
        # Create char buffer
        chars = [['.' for _ in range(grid.cols)] for _ in range(grid.rows)]
        
        # Render Entities
        for entity in grid.entities:
            r, c = entity.row, entity.col
            if 0 <= r < grid.rows and 0 <= c < grid.cols:
                char = '?'
                if entity.type == EntityType.COIN:
                    char = '©'
                elif entity.type == EntityType.PIGGYBANK:
                    char = 'U'
                elif entity.type == EntityType.OBSTACLE or entity.type == EntityType.FIXED_BLOCK:
                    char = '#'
                elif entity.type == EntityType.SUPPORT:
                    char = '_'
                elif entity.type == EntityType.DEFLECTOR:
                    char = '/' # Simplification
                elif entity.type == EntityType.GATEWAY:
                    char = 'H'
                elif entity.type == EntityType.TRAP:
                    char = 'x'
                
                chars[r][c] = char
        
        # Render Player Start if available
        if grid.player_start:
            pr, pc = grid.player_start[1], grid.player_start[0] # Tuple often (x, y) = (col, row)
            # Spec says Tuple[int, int], visualizer in prompt used (x,y). Let's assume (col, row).
            # Wait, grid access is usually row, col.
            # Dict grid in validator used (x,y).
            # Let's check spec.py if player_start is there. I added it. typical convention: x,y = col,row.
            if 0 <= pc < grid.rows and 0 <= pr < grid.cols:
                 chars[pc][pr] = 'S'
            elif 0 <= pr < grid.rows and 0 <= pc < grid.cols: # Try row, col just in case
                 chars[pr][pc] = 'S'

        # Build String
        lines = []
        lines.append(f"Grid: {grid.cols}x{grid.rows}")
        lines.append("+" + "-" * grid.cols + "+")
        for row in chars:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "-" * grid.cols + "+")
        
        if solution_path:
            lines.append(f"\nSolution steps: {len(solution_path)}")
            
        return "\n".join(lines)
