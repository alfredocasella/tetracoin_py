
import { notFound } from 'next/navigation';
import prisma from '@/lib/db';
import { GameContainer } from '@/components/game/game-container';
import { LevelConfig } from '@/lib/types';

export const dynamic = 'force-dynamic';

async function getLevel(levelNumber: number) {
  try {
    const level = await prisma.level.findUnique({
      where: { levelNumber },
    });
    return level;
  } catch (error) {
    console.error('Error fetching level:', error);
    return null;
  }
}

export default async function GamePage({ params }: { params: { levelNumber: string } }) {
  const levelNumber = parseInt(params?.levelNumber ?? '1', 10);
  const level = await getLevel(levelNumber);

  if (!level) {
    notFound();
  }

  const levelConfig: LevelConfig = {
    id: level.id,
    levelNumber: level.levelNumber,
    worldNumber: level.worldNumber,
    name: level.name,
    gridWidth: level.gridWidth,
    gridHeight: level.gridHeight,
    timeLimit: level.timeLimit,
    maxMovesForThreeStars: level.maxMovesForThreeStars,
    maxMovesForTwoStars: level.maxMovesForTwoStars,
    blocks: (level.blocks as any) ?? [],
    coins: (level.coins as any) ?? [],
    walls: (level.walls as any) ?? [],
  };

  return <GameContainer levelConfig={levelConfig} />;
}
