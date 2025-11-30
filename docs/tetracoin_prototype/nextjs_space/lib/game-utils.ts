
import { Block, Coin, Wall, Position, BLOCK_SHAPES } from './types';

export function getAbsoluteBlockPositions(block: Block): Position[] {
  const shape = BLOCK_SHAPES[block.shape];
  return shape?.map(cell => ({
    x: block.position.x + cell.x,
    y: block.position.y + cell.y,
  })) ?? [];
}

export function isPositionOccupied(
  position: Position,
  blocks: Block[],
  excludeBlockId?: string
): boolean {
  for (const block of blocks) {
    if (block.id === excludeBlockId) continue;
    const positions = getAbsoluteBlockPositions(block);
    if (positions.some(p => p.x === position.x && p.y === position.y)) {
      return true;
    }
  }
  return false;
}

export function isPositionWall(position: Position, walls: Wall[]): boolean {
  return walls?.some(wall => wall.position.x === position.x && wall.position.y === position.y) ?? false;
}

export function isValidBlockPosition(
  block: Block,
  gridWidth: number,
  gridHeight: number,
  blocks: Block[],
  walls: Wall[]
): boolean {
  const positions = getAbsoluteBlockPositions(block);
  
  for (const pos of positions) {
    // Check bounds
    if (pos.x < 0 || pos.x >= gridWidth || pos.y < 0 || pos.y >= gridHeight) {
      return false;
    }
    
    // Check wall collision
    if (isPositionWall(pos, walls)) {
      return false;
    }
    
    // Check block collision
    if (isPositionOccupied(pos, blocks, block.id)) {
      return false;
    }
  }
  
  return true;
}

export function collectCoinsAtPosition(
  block: Block,
  coins: Coin[]
): Coin[] {
  const blockPositions = getAbsoluteBlockPositions(block);
  const collectedCoins: Coin[] = [];
  
  for (const coin of coins) {
    const isOnBlock = blockPositions.some(
      pos => pos.x === coin.position.x && pos.y === coin.position.y
    );
    if (isOnBlock && coin.color === block.color) {
      collectedCoins.push(coin);
    }
  }
  
  return collectedCoins;
}

export function calculateStars(moves: number, threeStarMoves: number, twoStarMoves: number): number {
  if (moves <= threeStarMoves) return 3;
  if (moves <= twoStarMoves) return 2;
  return 1;
}

export function checkVictoryCondition(blocks: Block[], coins: Coin[]): boolean {
  // All blocks must be removed (counter = 0)
  const allBlocksRemoved = blocks.length === 0;
  
  // All coins must be collected
  const allCoinsCollected = coins.length === 0;
  
  return allBlocksRemoved && allCoinsCollected;
}

export function getCoinsByColor(coins: Coin[]): Record<string, number> {
  const result: Record<string, number> = {
    yellow: 0,
    blue: 0,
    red: 0,
    green: 0,
    purple: 0,
  };
  
  for (const coin of coins) {
    result[coin.color] = (result[coin.color] ?? 0) + 1;
  }
  
  return result;
}

export function getRequiredCoinsByColor(blocks: Block[]): Record<string, number> {
  const result: Record<string, number> = {
    yellow: 0,
    blue: 0,
    red: 0,
    green: 0,
    purple: 0,
  };
  
  for (const block of blocks) {
    result[block.color] = (result[block.color] ?? 0) + block.counter;
  }
  
  return result;
}
