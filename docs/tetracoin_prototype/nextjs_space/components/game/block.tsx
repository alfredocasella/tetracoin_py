
'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, PanInfo } from 'framer-motion';
import { Block as BlockType, BLOCK_COLORS, BLOCK_SHAPES } from '@/lib/types';

interface BlockProps {
  block: BlockType;
  cellSize: number;
  onDragEnd?: (event: any, info: PanInfo) => void;
}

export function Block({ block, cellSize, onDragEnd }: BlockProps) {
  const colors = BLOCK_COLORS[block.color];
  const shape = BLOCK_SHAPES[block.shape];
  const [isDragging, setIsDragging] = useState(false);

  if (!shape || !colors) return null;

  // Calculate bounding box
  const minX = Math.min(...(shape?.map(c => c?.x ?? 0) ?? [0]));
  const maxX = Math.max(...(shape?.map(c => c?.x ?? 0) ?? [0]));
  const minY = Math.min(...(shape?.map(c => c?.y ?? 0) ?? [0]));
  const maxY = Math.max(...(shape?.map(c => c?.y ?? 0) ?? [0]));

  const width = (maxX - minX + 1) * (cellSize + 4);
  const height = (maxY - minY + 1) * (cellSize + 4);

  return (
    <motion.div
      className="absolute cursor-grab active:cursor-grabbing touch-none select-none"
      style={{
        width,
        height,
        left: block.position.x * (cellSize + 4),
        top: block.position.y * (cellSize + 4),
        zIndex: isDragging ? 50 : 10,
      }}
      drag
      dragMomentum={false}
      dragElastic={0}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragSnapToOrigin={true}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={(event, info) => {
        setIsDragging(false);
        onDragEnd?.(event, info);
      }}
      whileHover={!isDragging ? { scale: 1.05 } : {}}
      whileDrag={{ scale: 1.1, opacity: 0.9 }}
      animate={
        !isDragging
          ? {
              y: [0, -2, 0],
              transition: { repeat: Infinity, duration: 2, ease: 'easeInOut' },
            }
          : {}
      }
    >
      {/* Block cells */}
      {(shape ?? []).map((cell, idx) => (
        <div
          key={idx}
          className="absolute rounded-lg shadow-md pointer-events-none"
          style={{
            width: cellSize,
            height: cellSize,
            left: ((cell?.x ?? 0) - minX) * (cellSize + 4),
            top: ((cell?.y ?? 0) - minY) * (cellSize + 4),
            background: `linear-gradient(180deg, 
              color-mix(in srgb, ${colors?.fill ?? '#FFC94D'} 110%, white),
              color-mix(in srgb, ${colors?.fill ?? '#FFC94D'} 90%, black)
            )`,
            border: `3px solid ${colors?.border ?? '#D9981F'}`,
          }}
        />
      ))}

      {/* Counter badge */}
      {(block?.counter ?? 0) > 0 && (
        <motion.div
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
          animate={
            (block?.counter ?? 0) <= 3
              ? {
                  scale: [1, 1.05, 1],
                  transition: {
                    repeat: Infinity,
                    duration: (block?.counter ?? 0) === 1 ? 0.8 : 1.5,
                  },
                }
              : {}
          }
        >
          <div
            className="rounded-full bg-white/90 border-2 shadow-lg flex items-center justify-center font-bold text-[#1A2130]"
            style={{
              width: cellSize * 0.9,
              height: cellSize * 0.9,
              fontSize: cellSize * 0.5,
              borderColor: colors?.border ?? '#D9981F',
              backgroundColor: (block?.counter ?? 0) === 1 ? `${colors?.fill ?? '#FFC94D'}CC` : undefined,
            }}
          >
            {block?.counter ?? 0}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
