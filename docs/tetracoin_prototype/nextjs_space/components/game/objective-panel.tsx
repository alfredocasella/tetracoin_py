
'use client';

import { motion } from 'framer-motion';
import { BlockColor, COIN_COLORS } from '@/lib/types';
import { Check, Sparkles } from 'lucide-react';

interface ObjectivePanelProps {
  objectives: Record<string, { collected: number; required: number }>;
}

const OBJECTIVE_BG_COLORS: Record<BlockColor, string> = {
  yellow: '#FFE8A3',
  blue: '#D7E3FF',
  red: '#FFD1D1',
  green: '#C4F1DD',
  purple: '#E4D1FF',
};

export function ObjectivePanel({ objectives }: ObjectivePanelProps) {
  const activeObjectives = Object.entries(objectives ?? {}).filter(
    ([_, data]) => (data?.required ?? 0) > 0
  );

  if (activeObjectives.length === 0) return null;

  return (
    <div className="w-full max-w-3xl mx-auto">
      <h3 className="text-2xl font-bold text-[#1A2130] mb-3 text-center">Obiettivi</h3>
      <div className="flex flex-wrap gap-3 justify-center">
        {activeObjectives.map(([color, data]) => {
          const coinColors = COIN_COLORS[color as BlockColor];
          const bgColor = OBJECTIVE_BG_COLORS[color as BlockColor];
          const isComplete = (data?.collected ?? 0) >= (data?.required ?? 0);

          return (
            <motion.div
              key={color}
              className="flex items-center gap-3 px-4 py-3 rounded-full shadow-md border-2"
              style={{
                backgroundColor: bgColor,
                borderColor: coinColors?.border ?? '#D9A842',
              }}
              animate={
                isComplete
                  ? {
                      scale: [1, 1.05, 1],
                      transition: { duration: 0.3 },
                    }
                  : {}
              }
            >
              <div
                className="w-8 h-8 rounded-full shadow-sm flex items-center justify-center"
                style={{
                  background: `radial-gradient(circle, ${coinColors?.fill ?? '#FFD66B'}, color-mix(in srgb, ${coinColors?.fill ?? '#FFD66B'} 80%, black))`,
                  border: `2px solid ${coinColors?.border ?? '#D9A842'}`,
                }}
              >
                <Sparkles className="w-4 h-4" style={{ color: coinColors?.border ?? '#D9A842' }} />
              </div>
              <span className="font-bold text-xl text-[#1A2130]">
                {data?.collected ?? 0} / {data?.required ?? 0}
              </span>
              {isComplete ? (
                <div className="w-6 h-6 rounded-full bg-[#33CC7A] flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" strokeWidth={3} />
                </div>
              ) : (
                <div className="w-6 h-6 rounded-full border-2 border-gray-400" />
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
