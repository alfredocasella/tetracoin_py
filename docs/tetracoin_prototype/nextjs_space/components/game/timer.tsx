
'use client';

import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

interface TimerProps {
  timeRemaining: number;
  totalTime: number;
}

export function Timer({ timeRemaining, totalTime }: TimerProps) {
  const percentage = totalTime > 0 ? timeRemaining / totalTime : 0;
  
  let timerColor = '#4F8BFF'; // Blue - normal
  let textColor = '#1A2130';
  
  if (percentage <= 0.2) {
    timerColor = '#FF5A5A'; // Red - critical
  } else if (percentage <= 0.5) {
    timerColor = '#FF9F43'; // Orange - warning
  }

  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;
  const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

  return (
    <motion.div
      className="flex items-center gap-2 px-6 py-3 bg-white rounded-full shadow-md border-2"
      style={{ borderColor: timerColor }}
      animate={
        percentage <= 0.2
          ? {
              scale: [1, 1.05, 1],
              transition: { repeat: Infinity, duration: 0.6 },
            }
          : {}
      }
    >
      <Clock className="w-6 h-6" style={{ color: timerColor }} />
      <span
        className="font-bold text-2xl"
        style={{ color: textColor }}
      >
        {timeString}
      </span>
    </motion.div>
  );
}
