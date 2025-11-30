
'use client';

import { motion } from 'framer-motion';
import { Coin as CoinType, COIN_COLORS } from '@/lib/types';
import { Sparkles } from 'lucide-react';

interface CoinProps {
  coin: CoinType;
  cellSize: number;
}

export function Coin({ coin, cellSize }: CoinProps) {
  const colors = COIN_COLORS[coin.color];

  if (!colors) return null;

  return (
    <motion.div
      className="absolute pointer-events-none flex items-center justify-center"
      style={{
        width: cellSize,
        height: cellSize,
        left: coin.position.x * (cellSize + 4),
        top: coin.position.y * (cellSize + 4),
        zIndex: 5,
      }}
      initial={{ scale: 0, rotate: -180 }}
      animate={{
        scale: [1, 1.1, 1],
        rotate: [0, 10, -10, 0],
        transition: {
          scale: { repeat: Infinity, duration: 2, ease: 'easeInOut' },
          rotate: { repeat: Infinity, duration: 3, ease: 'easeInOut' },
        },
      }}
    >
      <div
        className="w-4/5 h-4/5 rounded-full shadow-lg flex items-center justify-center"
        style={{
          background: `radial-gradient(circle at 30% 30%, 
            color-mix(in srgb, ${colors?.fill ?? '#FFD66B'} 120%, white),
            ${colors?.fill ?? '#FFD66B'}
          )`,
          border: `3px solid ${colors?.border ?? '#D9A842'}`,
        }}
      >
        <Sparkles
          className="w-1/2 h-1/2"
          style={{ color: colors?.border ?? '#D9A842' }}
          strokeWidth={3}
        />
      </div>
    </motion.div>
  );
}
