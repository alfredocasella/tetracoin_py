
'use client';

import { motion } from 'framer-motion';
import { XCircle, RotateCcw, Home } from 'lucide-react';

interface DefeatScreenProps {
  levelNumber: number;
  onRetry: () => void;
  onLevelSelect: () => void;
}

export function DefeatScreen({ levelNumber, onRetry, onLevelSelect }: DefeatScreenProps) {
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
          <XCircle className="w-16 h-16 mx-auto mb-3 text-[#FF5A5A]" />
          <h2 className="text-4xl font-bold text-[#FF5A5A] mb-2">TEMPO SCADUTO!</h2>
          <p className="text-lg text-gray-600">Livello {levelNumber}</p>
        </motion.div>

        {/* Message */}
        <motion.div
          className="bg-[#FFF5F5] rounded-2xl p-5 mb-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <p className="text-[#1A2130] text-lg">
            Il timer è scaduto prima che potessi completare il livello. Riprova!
          </p>
        </motion.div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <motion.button
            onClick={onRetry}
            className="w-full py-4 bg-[#00C2A8] text-white font-bold text-lg rounded-full shadow-lg flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <RotateCcw className="w-5 h-5" />
            Riprova
          </motion.button>
          <motion.button
            onClick={onLevelSelect}
            className="w-full py-3 bg-white border-2 border-gray-300 text-[#1A2130] font-bold rounded-full flex items-center justify-center gap-2"
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
