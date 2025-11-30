
'use client';

import { motion } from 'framer-motion';
import { RotateCcw } from 'lucide-react';

interface BottomBarProps {
  onReset: () => void;
  moves: number;
}

export function BottomBar({ onReset, moves }: BottomBarProps) {
  return (
    <div className="w-full bg-[#DCE7F9] rounded-t-3xl shadow-inner py-4 px-6">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Moves Counter */}
        <div className="flex items-center gap-2">
          <span className="text-lg font-medium text-[#1A2130]">Mosse:</span>
          <div className="px-4 py-2 bg-white rounded-full shadow-sm">
            <span className="font-bold text-xl text-[#1A2130]">{moves}</span>
          </div>
        </div>

        {/* Reset Button */}
        <motion.button
          onClick={onReset}
          className="w-20 h-20 rounded-full bg-[#4F8BFF]/80 flex items-center justify-center shadow-lg"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <RotateCcw className="w-10 h-10 text-white" strokeWidth={2.5} />
        </motion.button>
      </div>
    </div>
  );
}
