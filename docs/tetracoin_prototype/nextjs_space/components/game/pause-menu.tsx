
'use client';

import { motion } from 'framer-motion';
import { Play, RotateCcw, Home } from 'lucide-react';

interface PauseMenuProps {
  onResume: () => void;
  onRestart: () => void;
  onLevelSelect: () => void;
}

export function PauseMenu({ onResume, onRestart, onLevelSelect }: PauseMenuProps) {
  return (
    <motion.div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <motion.div
        className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 400 }}
      >
        <h2 className="text-3xl font-bold text-[#1A2130] mb-6 text-center">Pausa</h2>

        <div className="space-y-3">
          <motion.button
            onClick={onResume}
            className="w-full py-4 bg-[#00C2A8] text-white font-bold text-lg rounded-full shadow-lg flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Play className="w-5 h-5" fill="white" />
            Riprendi
          </motion.button>
          <motion.button
            onClick={onRestart}
            className="w-full py-4 bg-white border-2 border-[#4F8BFF] text-[#4F8BFF] font-bold text-lg rounded-full flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <RotateCcw className="w-5 h-5" />
            Ricomincia
          </motion.button>
          <motion.button
            onClick={onLevelSelect}
            className="w-full py-4 bg-white border-2 border-gray-300 text-[#1A2130] font-bold text-lg rounded-full flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Home className="w-5 h-5" />
            Selezione Livelli
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
}
