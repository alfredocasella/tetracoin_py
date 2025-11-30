
'use client';

import { motion } from 'framer-motion';
import { Pause, RotateCcw } from 'lucide-react';
import { Timer } from './timer';

interface HUDProps {
  levelNumber: number;
  worldNumber: number;
  timeRemaining: number;
  totalTime: number;
  onPause: () => void;
  onReset: () => void;
}

export function HUD({ levelNumber, worldNumber, timeRemaining, totalTime, onPause, onReset }: HUDProps) {
  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* Top HUD */}
      <div className="flex items-center justify-between mb-4 px-4">
        {/* Level Info */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#00C2A8] flex items-center justify-center text-white font-bold">
            {worldNumber}
          </div>
          <span className="font-bold text-xl text-[#1A2130]">
            Mondo {worldNumber} - Livello {levelNumber}
          </span>
        </div>

        {/* Timer */}
        <Timer timeRemaining={timeRemaining} totalTime={totalTime} />

        {/* Pause Button */}
        <motion.button
          onClick={onPause}
          className="w-14 h-14 rounded-full bg-[#00C2A8] flex items-center justify-center shadow-lg"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <Pause className="w-8 h-8 text-white" fill="white" />
        </motion.button>
      </div>
    </div>
  );
}
