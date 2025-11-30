
export type BlockColor = 'yellow' | 'blue' | 'red' | 'green' | 'purple';
export type BlockShape = 'I4' | 'O4' | 'L4' | 'T4' | 'J4' | 'S4' | 'Z4' | 'I3' | 'L3';

export interface Position {
  x: number;
  y: number;
}

export interface Block {
  id: string;
  shape: BlockShape;
  color: BlockColor;
  position: Position;
  counter: number;
  cells: Position[]; // Relative positions
}

export interface Coin {
  id: string;
  color: BlockColor;
  position: Position;
}

export interface Wall {
  position: Position;
}

export interface LevelConfig {
  id: string;
  levelNumber: number;
  worldNumber: number;
  name: string;
  gridWidth: number;
  gridHeight: number;
  timeLimit: number;
  maxMovesForThreeStars: number;
  maxMovesForTwoStars: number;
  blocks: Omit<Block, 'id'>[];
  coins: Omit<Coin, 'id'>[];
  walls: Wall[];
}

export interface GameState {
  blocks: Block[];
  coins: Coin[];
  walls: Wall[];
  moves: number;
  timeRemaining: number;
  isPlaying: boolean;
  isPaused: boolean;
  gameResult: 'none' | 'victory' | 'defeat';
}

export const BLOCK_SHAPES: Record<BlockShape, Position[]> = {
  I4: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }],
  O4: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
  L4: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 0, y: 2 }, { x: 1, y: 0 }],
  J4: [{ x: 1, y: 0 }, { x: 1, y: 1 }, { x: 1, y: 2 }, { x: 0, y: 0 }],
  T4: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 1 }],
  S4: [{ x: 1, y: 0 }, { x: 2, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
  Z4: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 1 }],
  I3: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }],
  L3: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 0 }],
};

export const BLOCK_COLORS: Record<BlockColor, { fill: string; border: string }> = {
  yellow: { fill: '#FFC94D', border: '#D9981F' },
  blue: { fill: '#4F8BFF', border: '#2A57BF' },
  red: { fill: '#FF5A5A', border: '#C23030' },
  green: { fill: '#33CC7A', border: '#229957' },
  purple: { fill: '#B870FF', border: '#7C3AC2' },
};

export const COIN_COLORS: Record<BlockColor, { fill: string; border: string }> = {
  yellow: { fill: '#FFD66B', border: '#D9A842' },
  blue: { fill: '#6BA0FF', border: '#3E6BD9' },
  red: { fill: '#FF7A7A', border: '#D94747' },
  green: { fill: '#4DDE8A', border: '#2EAA60' },
  purple: { fill: '#C88AFF', border: '#8A4BD9' },
};
