
'use client';

import { useState, useCallback, useEffect } from 'react';
import { Block, Coin, Wall, Position, LevelConfig, GameState } from '@/lib/types';
import {
  getAbsoluteBlockPositions,
  isValidBlockPosition,
  collectCoinsAtPosition,
  checkVictoryCondition,
} from '@/lib/game-utils';

export function useGameState(levelConfig: LevelConfig | null) {
  const [gameState, setGameState] = useState<GameState>({
    blocks: [],
    coins: [],
    walls: [],
    moves: 0,
    timeRemaining: 0,
    isPlaying: false,
    isPaused: false,
    gameResult: 'none',
  });

  const [initialState, setInitialState] = useState<GameState | null>(null);

  // Initialize game from level config
  useEffect(() => {
    if (!levelConfig) return;

    const blocks: Block[] = (levelConfig.blocks ?? []).map((b, idx) => ({
      id: `block-${idx}`,
      shape: b.shape,
      color: b.color,
      position: b.position,
      counter: b.counter,
      cells: b.cells,
    }));

    const coins: Coin[] = (levelConfig.coins ?? []).map((c, idx) => ({
      id: `coin-${idx}`,
      color: c.color,
      position: c.position,
    }));

    const walls: Wall[] = levelConfig.walls ?? [];

    const initialGameState: GameState = {
      blocks,
      coins,
      walls,
      moves: 0,
      timeRemaining: levelConfig.timeLimit,
      isPlaying: true,
      isPaused: false,
      gameResult: 'none',
    };

    setGameState(initialGameState);
    setInitialState(initialGameState);
  }, [levelConfig]);

  const moveBlock = useCallback(
    (blockId: string, newPosition: Position) => {
      if (!levelConfig) return false;

      setGameState(prev => {
        if (!prev.isPlaying || prev.isPaused || prev.gameResult !== 'none') {
          return prev;
        }

        const block = prev.blocks?.find(b => b.id === blockId);
        if (!block) return prev;

        // Create updated block with new position
        const updatedBlock = { ...block, position: newPosition };

        // Validate position
        if (
          !isValidBlockPosition(
            updatedBlock,
            levelConfig.gridWidth,
            levelConfig.gridHeight,
            prev.blocks ?? [],
            prev.walls ?? []
          )
        ) {
          return prev;
        }

        // Collect coins
        const collectedCoins = collectCoinsAtPosition(updatedBlock, prev.coins ?? []);
        const remainingCoins = (prev.coins ?? []).filter(
          c => !collectedCoins.some(cc => cc.id === c.id)
        );

        // Update block counter
        const newCounter = block.counter - collectedCoins.length;
        const finalBlock = { ...updatedBlock, counter: newCounter };

        // Remove block if counter reaches 0
        const updatedBlocks = newCounter <= 0
          ? (prev.blocks ?? []).filter(b => b.id !== blockId)
          : (prev.blocks ?? []).map(b => (b.id === blockId ? finalBlock : b));

        const newMoves = prev.moves + 1;

        // Check victory
        const isVictory = checkVictoryCondition(updatedBlocks, remainingCoins);

        return {
          ...prev,
          blocks: updatedBlocks,
          coins: remainingCoins,
          moves: newMoves,
          gameResult: isVictory ? 'victory' : 'none',
          isPlaying: !isVictory,
        };
      });

      return true;
    },
    [levelConfig]
  );

  const resetLevel = useCallback(() => {
    if (initialState) {
      setGameState(initialState);
    }
  }, [initialState]);

  const pauseGame = useCallback(() => {
    setGameState(prev => ({ ...prev, isPaused: true }));
  }, []);

  const resumeGame = useCallback(() => {
    setGameState(prev => ({ ...prev, isPaused: false }));
  }, []);

  const updateTimeRemaining = useCallback((time: number) => {
    setGameState(prev => {
      if (!prev.isPlaying || prev.isPaused || prev.gameResult !== 'none') {
        return prev;
      }

      if (time <= 0) {
        return {
          ...prev,
          timeRemaining: 0,
          isPlaying: false,
          gameResult: 'defeat',
        };
      }

      return { ...prev, timeRemaining: time };
    });
  }, []);

  return {
    gameState,
    moveBlock,
    resetLevel,
    pauseGame,
    resumeGame,
    updateTimeRemaining,
  };
}
