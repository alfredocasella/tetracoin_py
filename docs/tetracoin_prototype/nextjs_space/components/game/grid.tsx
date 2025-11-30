
'use client';

import { motion } from 'framer-motion';
import { Wall } from '@/lib/types';

interface GridProps {
  width: number;
  height: number;
  walls: Wall[];
  cellSize: number;
}

export function Grid({ width, height, walls, cellSize }: GridProps) {
  const gridCells: JSX.Element[] = [];

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const isWall = walls?.some(w => w.position.x === x && w.position.y === y) ?? false;

      gridCells.push(
        <motion.div
          key={`cell-${x}-${y}`}
          className={`
            rounded-lg border-2
            ${isWall 
              ? 'bg-[#8A8FA0] border-[#7A8190]' 
              : 'bg-[#EAF1FF] border-[#D0D7E2] border-opacity-50'
            }
          `}
          style={{
            width: cellSize,
            height: cellSize,
            gridColumn: x + 1,
            gridRow: y + 1,
          }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: (y * width + x) * 0.01, duration: 0.2 }}
        />
      );
    }
  }

  return (
    <div
      className="grid gap-1 bg-[#F5F9FF] p-3 rounded-3xl border-2 border-[#D0D7E2] shadow-lg"
      style={{
        gridTemplateColumns: `repeat(${width}, ${cellSize}px)`,
        gridTemplateRows: `repeat(${height}, ${cellSize}px)`,
      }}
    >
      {gridCells}
    </div>
  );
}
