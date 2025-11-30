
'use client';

import { motion } from 'framer-motion';
import { Star, Trophy, Clock, Move } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface VictoryScreenProps {
  stars: number;
  moves: number;
  timeRemaining: number;
  levelNumber: number;
  onNextLevel?: () => void;
  onRetry: () => void;
  onLevelSelect: () => void;
}

export function VictoryScreen({
  stars,
  moves,
  timeRemaining,
  levelNumber,
  onNextLevel,
  onRetry,
  onLevelSelect,
}: VictoryScreenProps) {
  const router = useRouter();
  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;

  return (
    <motion.div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full"
        initial={{ scale: 0.8, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
      >
        {/* Header */}
        <motion.div
          className="text-center mb-6"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Trophy className="w-16 h-16 mx-auto mb-3 text-[#33CC7A]" />
          <h2 className="text-4xl font-bold text-[#33CC7A] mb-2">LIVELLO COMPLETATO!</h2>
          <p className="text-lg text-gray-600">Livello {levelNumber}</p>
        </motion.div>

        {/* Stars */}
        <div className="flex justify-center gap-4 mb-6">
          {[1, 2, 3].map((index) => (
            <motion.div
              key={index}
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{
                delay: 0.4 + index * 0.2,
                type: 'spring',
                damping: 15,
              }}
            >
              <Star
                className="w-16 h-16"
                fill={index <= stars ? '#FFD66B' : 'none'}
                stroke={index <= stars ? '#D9A842' : '#D0D7E2'}
                strokeWidth={2}
              />
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <motion.div
          className="bg-[#F5F9FF] rounded-2xl p-5 mb-6 space-y-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Move className="w-5 h-5 text-[#4F8BFF]" />
              <span className="font-medium text-[#1A2130]">Mosse usate:</span>
            </div>
            <span className="font-bold text-xl text-[#1A2130]">{moves}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-[#4F8BFF]" />
              <span className="font-medium text-[#1A2130]">Tempo rimanente:</span>
            </div>
            <span className="font-bold text-xl text-[#1A2130]">
              {minutes}:{seconds.toString().padStart(2, '0')}
            </span>
          </div>
        </motion.div>

        {/* Action Buttons */}
        <div className="space-y-3">
          {onNextLevel && (
            <motion.button
              onClick={onNextLevel}
              className="w-full py-4 bg-[#00C2A8] text-white font-bold text-lg rounded-full shadow-lg"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Livello Successivo
            </motion.button>
          )}
          <div className="flex gap-3">
            <motion.button
              onClick={onRetry}
              className="flex-1 py-3 bg-white border-2 border-[#4F8BFF] text-[#4F8BFF] font-bold rounded-full"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Riprova
            </motion.button>
            <motion.button
              onClick={onLevelSelect}
              className="flex-1 py-3 bg-white border-2 border-gray-300 text-[#1A2130] font-bold rounded-full"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Selezione Livelli
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
