
'use client';

import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { LevelConfig, Block as BlockType, Position } from '@/lib/types';
import { useGameState } from '@/hooks/use-game-state';
import { useTimer } from '@/hooks/use-timer';
import { calculateStars, getCoinsByColor, getRequiredCoinsByColor } from '@/lib/game-utils';
import { Grid } from './grid';
import { Block } from './block';
import { Coin } from './coin';
import { HUD } from './hud';
import { ObjectivePanel } from './objective-panel';
import { BottomBar } from './bottom-bar';
import { VictoryScreen } from './victory-screen';
import { DefeatScreen } from './defeat-screen';
import { PauseMenu } from './pause-menu';

interface GameContainerProps {
  levelConfig: LevelConfig;
}

export function GameContainer({ levelConfig }: GameContainerProps) {
  const router = useRouter();
  const [showPauseMenu, setShowPauseMenu] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { gameState, moveBlock, resetLevel, pauseGame, resumeGame, updateTimeRemaining } =
    useGameState(levelConfig);

  const isTimerActive =
    gameState?.isPlaying === true &&
    gameState?.isPaused === false &&
    gameState?.gameResult === 'none';

  useTimer(isTimerActive, gameState?.timeRemaining ?? 0, updateTimeRemaining);

  const cellSize = 60; // Base cell size

  const handlePause = useCallback(() => {
    pauseGame();
    setShowPauseMenu(true);
  }, [pauseGame]);

  const handleResume = useCallback(() => {
    resumeGame();
    setShowPauseMenu(false);
  }, [resumeGame]);

  const handleReset = useCallback(() => {
    resetLevel();
    setShowPauseMenu(false);
  }, [resetLevel]);

  const handleLevelSelect = useCallback(() => {
    router.push('/levels');
  }, [router]);

  const handleNextLevel = useCallback(() => {
    const nextLevelNumber = (levelConfig?.levelNumber ?? 0) + 1;
    router.push(`/game/${nextLevelNumber}`);
  }, [levelConfig, router]);

  const handleDragEnd = useCallback(
    (blockId: string, event: any, info: any) => {
      if (!containerRef.current) {
        return;
      }

      const gridElement = containerRef.current.querySelector('.grid-container');
      if (!gridElement) {
        return;
      }

      const block = (gameState?.blocks ?? []).find(b => b?.id === blockId);
      if (!block) return;

      const rect = gridElement.getBoundingClientRect();
      
      // Get the center point of the block after drag
      const blockCenterX = block.position.x * (cellSize + 4) + info.offset.x;
      const blockCenterY = block.position.y * (cellSize + 4) + info.offset.y;

      // Convert to grid coordinates
      const gridX = Math.round(blockCenterX / (cellSize + 4));
      const gridY = Math.round(blockCenterY / (cellSize + 4));

      const newPosition: Position = {
        x: Math.max(0, Math.min(gridX, (levelConfig?.gridWidth ?? 6) - 1)),
        y: Math.max(0, Math.min(gridY, (levelConfig?.gridHeight ?? 6) - 1)),
      };

      // Try to move the block
      moveBlock(blockId, newPosition);
    },
    [moveBlock, levelConfig, cellSize, gameState]
  );

  // Calculate objectives
  const remainingCoinsByColor = getCoinsByColor(gameState?.coins ?? []);
  const requiredCoinsByColor = getRequiredCoinsByColor(
    levelConfig?.blocks?.map((b, i) => ({
      id: `block-${i}`,
      ...b,
      cells: [],
    })) ?? []
  );

  const objectives = Object.keys(requiredCoinsByColor).reduce((acc, color) => {
    const required = requiredCoinsByColor[color] ?? 0;
    const remaining = remainingCoinsByColor[color] ?? 0;
    const collected = required - remaining;
    
    acc[color] = { collected, required };
    return acc;
  }, {} as Record<string, { collected: number; required: number }>);

  const stars =
    gameState?.gameResult === 'victory'
      ? calculateStars(
          gameState?.moves ?? 0,
          levelConfig?.maxMovesForThreeStars ?? 0,
          levelConfig?.maxMovesForTwoStars ?? 0
        )
      : 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#F2F7FF] to-[#DCE7F9] flex flex-col py-4 px-2">
      {/* HUD */}
      <HUD
        levelNumber={levelConfig?.levelNumber ?? 1}
        worldNumber={levelConfig?.worldNumber ?? 1}
        timeRemaining={gameState?.timeRemaining ?? 0}
        totalTime={levelConfig?.timeLimit ?? 180}
        onPause={handlePause}
        onReset={handleReset}
      />

      {/* Game Area */}
      <div className="flex-1 flex items-center justify-center py-6" ref={containerRef}>
        <div className="relative grid-container">
          <Grid
            width={levelConfig?.gridWidth ?? 6}
            height={levelConfig?.gridHeight ?? 6}
            walls={gameState?.walls ?? []}
            cellSize={cellSize}
          />

          {/* Coins */}
          <div className="absolute inset-0 pointer-events-none" style={{ padding: 12 }}>
            {(gameState?.coins ?? []).map(coin => (
              <Coin key={coin.id} coin={coin} cellSize={cellSize} />
            ))}
          </div>

          {/* Blocks */}
          <div className="absolute inset-0" style={{ padding: 12 }}>
            {(gameState?.blocks ?? []).map(block => (
              <Block
                key={block?.id ?? 'block'}
                block={block}
                cellSize={cellSize}
                onDragEnd={(event: any, info: any) => handleDragEnd(block?.id ?? '', event, info)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Objective Panel */}
      <div className="py-4">
        <ObjectivePanel objectives={objectives} />
      </div>

      {/* Bottom Bar */}
      <BottomBar onReset={handleReset} moves={gameState?.moves ?? 0} />

      {/* Pause Menu */}
      {showPauseMenu && (
        <PauseMenu
          onResume={handleResume}
          onRestart={handleReset}
          onLevelSelect={handleLevelSelect}
        />
      )}

      {/* Victory Screen */}
      {gameState?.gameResult === 'victory' && (
        <VictoryScreen
          stars={stars}
          moves={gameState?.moves ?? 0}
          timeRemaining={gameState?.timeRemaining ?? 0}
          levelNumber={levelConfig?.levelNumber ?? 1}
          onNextLevel={handleNextLevel}
          onRetry={handleReset}
          onLevelSelect={handleLevelSelect}
        />
      )}

      {/* Defeat Screen */}
      {gameState?.gameResult === 'defeat' && (
        <DefeatScreen
          levelNumber={levelConfig?.levelNumber ?? 1}
          onRetry={handleReset}
          onLevelSelect={handleLevelSelect}
        />
      )}
    </div>
  );
}
