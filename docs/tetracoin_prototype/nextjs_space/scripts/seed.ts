
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const LEVELS = [
  // Level 1 - Tutorial: Simple I4 block, 4 yellow coins
  {
    levelNumber: 1,
    worldNumber: 1,
    name: 'Primi Passi',
    gridWidth: 6,
    gridHeight: 6,
    timeLimit: 180,
    maxMovesForThreeStars: 2,
    maxMovesForTwoStars: 3,
    blocks: [
      {
        shape: 'I4',
        color: 'yellow',
        position: { x: 1, y: 4 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }],
      },
    ],
    coins: [
      { color: 'yellow', position: { x: 1, y: 1 } },
      { color: 'yellow', position: { x: 2, y: 1 } },
      { color: 'yellow', position: { x: 3, y: 1 } },
      { color: 'yellow', position: { x: 4, y: 1 } },
    ],
    walls: [],
  },
  // Level 2 - Two colors
  {
    levelNumber: 2,
    worldNumber: 1,
    name: 'Due Colori',
    gridWidth: 6,
    gridHeight: 6,
    timeLimit: 180,
    maxMovesForThreeStars: 3,
    maxMovesForTwoStars: 5,
    blocks: [
      {
        shape: 'I3',
        color: 'yellow',
        position: { x: 0, y: 0 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }],
      },
      {
        shape: 'L3',
        color: 'blue',
        position: { x: 3, y: 4 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 0 }],
      },
    ],
    coins: [
      { color: 'yellow', position: { x: 1, y: 2 } },
      { color: 'yellow', position: { x: 2, y: 2 } },
      { color: 'yellow', position: { x: 3, y: 2 } },
      { color: 'blue', position: { x: 1, y: 4 } },
      { color: 'blue', position: { x: 1, y: 5 } },
      { color: 'blue', position: { x: 2, y: 4 } },
    ],
    walls: [],
  },
  // Level 3 - O4 block with walls
  {
    levelNumber: 3,
    worldNumber: 1,
    name: 'Primi Ostacoli',
    gridWidth: 6,
    gridHeight: 6,
    timeLimit: 150,
    maxMovesForThreeStars: 2,
    maxMovesForTwoStars: 4,
    blocks: [
      {
        shape: 'O4',
        color: 'red',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
      },
    ],
    coins: [
      { color: 'red', position: { x: 3, y: 3 } },
      { color: 'red', position: { x: 4, y: 3 } },
      { color: 'red', position: { x: 3, y: 4 } },
      { color: 'red', position: { x: 4, y: 4 } },
    ],
    walls: [
      { position: { x: 2, y: 2 } },
      { position: { x: 2, y: 3 } },
      { position: { x: 3, y: 2 } },
    ],
  },
  // Level 4 - L4 shape
  {
    levelNumber: 4,
    worldNumber: 1,
    name: 'Forma a L',
    gridWidth: 7,
    gridHeight: 7,
    timeLimit: 150,
    maxMovesForThreeStars: 3,
    maxMovesForTwoStars: 5,
    blocks: [
      {
        shape: 'L4',
        color: 'green',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 0, y: 2 }, { x: 1, y: 0 }],
      },
    ],
    coins: [
      { color: 'green', position: { x: 4, y: 2 } },
      { color: 'green', position: { x: 4, y: 3 } },
      { color: 'green', position: { x: 4, y: 4 } },
      { color: 'green', position: { x: 5, y: 2 } },
    ],
    walls: [
      { position: { x: 3, y: 1 } },
      { position: { x: 3, y: 2 } },
      { position: { x: 3, y: 3 } },
      { position: { x: 3, y: 4 } },
      { position: { x: 3, y: 5 } },
    ],
  },
  // Level 5 - T4 shape with multiple colors
  {
    levelNumber: 5,
    worldNumber: 1,
    name: 'Forma a T',
    gridWidth: 7,
    gridHeight: 7,
    timeLimit: 150,
    maxMovesForThreeStars: 4,
    maxMovesForTwoStars: 6,
    blocks: [
      {
        shape: 'T4',
        color: 'purple',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 1 }],
      },
      {
        shape: 'I3',
        color: 'yellow',
        position: { x: 4, y: 5 },
        counter: 2,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }],
      },
    ],
    coins: [
      { color: 'purple', position: { x: 2, y: 3 } },
      { color: 'purple', position: { x: 3, y: 3 } },
      { color: 'purple', position: { x: 4, y: 3 } },
      { color: 'purple', position: { x: 3, y: 4 } },
      { color: 'yellow', position: { x: 1, y: 5 } },
      { color: 'yellow', position: { x: 2, y: 5 } },
    ],
    walls: [
      { position: { x: 0, y: 3 } },
      { position: { x: 1, y: 3 } },
      { position: { x: 5, y: 3 } },
      { position: { x: 6, y: 3 } },
    ],
  },
  // Level 6 - Multiple blocks, more complex
  {
    levelNumber: 6,
    worldNumber: 1,
    name: 'Incastro Perfetto',
    gridWidth: 7,
    gridHeight: 7,
    timeLimit: 120,
    maxMovesForThreeStars: 5,
    maxMovesForTwoStars: 8,
    blocks: [
      {
        shape: 'I4',
        color: 'blue',
        position: { x: 0, y: 0 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }],
      },
      {
        shape: 'O4',
        color: 'red',
        position: { x: 5, y: 0 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
      },
      {
        shape: 'L3',
        color: 'green',
        position: { x: 0, y: 5 },
        counter: 2,
        cells: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 0 }],
      },
    ],
    coins: [
      { color: 'blue', position: { x: 1, y: 3 } },
      { color: 'blue', position: { x: 2, y: 3 } },
      { color: 'blue', position: { x: 3, y: 3 } },
      { color: 'red', position: { x: 4, y: 4 } },
      { color: 'red', position: { x: 5, y: 4 } },
      { color: 'red', position: { x: 4, y: 5 } },
      { color: 'green', position: { x: 3, y: 5 } },
      { color: 'green', position: { x: 3, y: 6 } },
    ],
    walls: [
      { position: { x: 0, y: 3 } },
      { position: { x: 6, y: 3 } },
      { position: { x: 3, y: 0 } },
      { position: { x: 3, y: 1 } },
      { position: { x: 3, y: 2 } },
    ],
  },
  // Level 7 - J4 shape
  {
    levelNumber: 7,
    worldNumber: 1,
    name: 'Sfida a J',
    gridWidth: 7,
    gridHeight: 7,
    timeLimit: 120,
    maxMovesForThreeStars: 4,
    maxMovesForTwoStars: 6,
    blocks: [
      {
        shape: 'J4',
        color: 'yellow',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 1, y: 0 }, { x: 1, y: 1 }, { x: 1, y: 2 }, { x: 0, y: 0 }],
      },
      {
        shape: 'I3',
        color: 'blue',
        position: { x: 4, y: 0 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }],
      },
    ],
    coins: [
      { color: 'yellow', position: { x: 3, y: 4 } },
      { color: 'yellow', position: { x: 4, y: 4 } },
      { color: 'yellow', position: { x: 4, y: 5 } },
      { color: 'yellow', position: { x: 4, y: 6 } },
      { color: 'blue', position: { x: 0, y: 4 } },
      { color: 'blue', position: { x: 1, y: 4 } },
      { color: 'blue', position: { x: 2, y: 4 } },
    ],
    walls: [
      { position: { x: 3, y: 0 } },
      { position: { x: 3, y: 1 } },
      { position: { x: 3, y: 2 } },
      { position: { x: 3, y: 3 } },
    ],
  },
  // Level 8 - S4 and Z4 shapes
  {
    levelNumber: 8,
    worldNumber: 1,
    name: 'Zig-Zag',
    gridWidth: 8,
    gridHeight: 8,
    timeLimit: 120,
    maxMovesForThreeStars: 5,
    maxMovesForTwoStars: 7,
    blocks: [
      {
        shape: 'S4',
        color: 'red',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 1, y: 0 }, { x: 2, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
      },
      {
        shape: 'Z4',
        color: 'green',
        position: { x: 5, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 1 }],
      },
    ],
    coins: [
      { color: 'red', position: { x: 3, y: 4 } },
      { color: 'red', position: { x: 4, y: 4 } },
      { color: 'red', position: { x: 2, y: 5 } },
      { color: 'red', position: { x: 3, y: 5 } },
      { color: 'green', position: { x: 4, y: 6 } },
      { color: 'green', position: { x: 5, y: 6 } },
      { color: 'green', position: { x: 5, y: 7 } },
      { color: 'green', position: { x: 6, y: 7 } },
    ],
    walls: [
      { position: { x: 0, y: 4 } },
      { position: { x: 1, y: 4 } },
      { position: { x: 6, y: 4 } },
      { position: { x: 7, y: 4 } },
    ],
  },
  // Level 9 - Complex puzzle
  {
    levelNumber: 9,
    worldNumber: 1,
    name: 'Puzzle Complesso',
    gridWidth: 8,
    gridHeight: 8,
    timeLimit: 100,
    maxMovesForThreeStars: 8,
    maxMovesForTwoStars: 12,
    blocks: [
      {
        shape: 'T4',
        color: 'purple',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 1 }],
      },
      {
        shape: 'L4',
        color: 'yellow',
        position: { x: 5, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 0, y: 2 }, { x: 1, y: 0 }],
      },
      {
        shape: 'O4',
        color: 'blue',
        position: { x: 0, y: 6 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
      },
    ],
    coins: [
      { color: 'purple', position: { x: 2, y: 4 } },
      { color: 'purple', position: { x: 3, y: 4 } },
      { color: 'purple', position: { x: 4, y: 4 } },
      { color: 'purple', position: { x: 3, y: 5 } },
      { color: 'yellow', position: { x: 5, y: 5 } },
      { color: 'yellow', position: { x: 5, y: 6 } },
      { color: 'yellow', position: { x: 5, y: 7 } },
      { color: 'yellow', position: { x: 6, y: 5 } },
      { color: 'blue', position: { x: 3, y: 7 } },
      { color: 'blue', position: { x: 4, y: 7 } },
      { color: 'blue', position: { x: 4, y: 6 } },
    ],
    walls: [
      { position: { x: 0, y: 4 } },
      { position: { x: 1, y: 4 } },
      { position: { x: 6, y: 4 } },
      { position: { x: 7, y: 4 } },
      { position: { x: 4, y: 0 } },
      { position: { x: 4, y: 1 } },
      { position: { x: 4, y: 2 } },
      { position: { x: 4, y: 3 } },
    ],
  },
  // Level 10 - Final challenge
  {
    levelNumber: 10,
    worldNumber: 1,
    name: 'Sfida Finale',
    gridWidth: 8,
    gridHeight: 8,
    timeLimit: 90,
    maxMovesForThreeStars: 10,
    maxMovesForTwoStars: 15,
    blocks: [
      {
        shape: 'I4',
        color: 'red',
        position: { x: 0, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }],
      },
      {
        shape: 'T4',
        color: 'green',
        position: { x: 4, y: 0 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 1 }],
      },
      {
        shape: 'L4',
        color: 'blue',
        position: { x: 0, y: 4 },
        counter: 4,
        cells: [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 0, y: 2 }, { x: 1, y: 0 }],
      },
      {
        shape: 'O4',
        color: 'yellow',
        position: { x: 6, y: 4 },
        counter: 3,
        cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }],
      },
    ],
    coins: [
      { color: 'red', position: { x: 2, y: 5 } },
      { color: 'red', position: { x: 3, y: 5 } },
      { color: 'red', position: { x: 4, y: 5 } },
      { color: 'red', position: { x: 5, y: 5 } },
      { color: 'green', position: { x: 2, y: 6 } },
      { color: 'green', position: { x: 3, y: 6 } },
      { color: 'green', position: { x: 4, y: 6 } },
      { color: 'green', position: { x: 3, y: 7 } },
      { color: 'blue', position: { x: 4, y: 2 } },
      { color: 'blue', position: { x: 4, y: 3 } },
      { color: 'blue', position: { x: 4, y: 4 } },
      { color: 'blue', position: { x: 5, y: 2 } },
      { color: 'yellow', position: { x: 6, y: 6 } },
      { color: 'yellow', position: { x: 7, y: 6 } },
      { color: 'yellow', position: { x: 7, y: 7 } },
    ],
    walls: [
      { position: { x: 0, y: 2 } },
      { position: { x: 1, y: 2 } },
      { position: { x: 2, y: 2 } },
      { position: { x: 6, y: 2 } },
      { position: { x: 7, y: 2 } },
      { position: { x: 3, y: 3 } },
      { position: { x: 3, y: 4 } },
      { position: { x: 5, y: 7 } },
    ],
  },
];

async function main() {
  console.log('🌱 Starting database seeding...');

  // Clear existing data
  console.log('🗑️  Clearing existing data...');
  await prisma.userProgress.deleteMany({});
  await prisma.level.deleteMany({});

  // Seed levels
  console.log('📊 Seeding levels...');
  for (const levelData of LEVELS) {
    await prisma.level.create({
      data: {
        levelNumber: levelData.levelNumber,
        worldNumber: levelData.worldNumber,
        name: levelData.name,
        gridWidth: levelData.gridWidth,
        gridHeight: levelData.gridHeight,
        timeLimit: levelData.timeLimit,
        maxMovesForThreeStars: levelData.maxMovesForThreeStars,
        maxMovesForTwoStars: levelData.maxMovesForTwoStars,
        blocks: levelData.blocks,
        coins: levelData.coins,
        walls: levelData.walls,
      },
    });
    console.log(`  ✅ Level ${levelData.levelNumber}: ${levelData.name}`);
  }

  console.log('✨ Database seeding completed!');
}

main()
  .catch((e) => {
    console.error('❌ Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
