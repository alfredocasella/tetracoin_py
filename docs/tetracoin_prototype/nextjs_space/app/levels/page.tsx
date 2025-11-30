
import Link from 'next/link';
import { ArrowLeft, Star, Lock } from 'lucide-react';
import prisma from '@/lib/db';

export const dynamic = 'force-dynamic';

async function getLevels() {
  try {
    const levels = await prisma.level.findMany({
      orderBy: [{ worldNumber: 'asc' }, { levelNumber: 'asc' }],
    });
    return levels;
  } catch (error) {
    console.error('Error fetching levels:', error);
    return [];
  }
}

export default async function LevelsPage() {
  const levels = await getLevels();

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#F2F7FF] to-[#DCE7F9] py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link
            href="/"
            className="flex items-center gap-2 text-[#1A2130] font-bold text-lg hover:text-[#00C2A8] transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
            Menu Principale
          </Link>
          <h1 className="text-4xl font-bold text-[#1A2130]">Seleziona Livello</h1>
          <div className="w-32" /> {/* Spacer for centering */}
        </div>

        {/* Levels Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {levels?.map((level: any) => {
            const isLocked = false; // In a real app, check user progress

            return (
              <Link
                key={level?.id ?? 'level'}
                href={isLocked ? '#' : `/game/${level?.levelNumber ?? 1}`}
                className={`
                  group relative bg-white rounded-3xl p-6 shadow-lg transition-all duration-200
                  ${isLocked 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:scale-105 hover:shadow-2xl cursor-pointer'
                  }
                `}
              >
                {/* Level Number */}
                <div className="text-center mb-4">
                  <div className="text-5xl font-bold text-[#00C2A8] mb-2">
                    {level?.levelNumber ?? 1}
                  </div>
                  <p className="text-sm font-medium text-gray-600 line-clamp-1">
                    {level?.name ?? 'Livello'}
                  </p>
                </div>

                {/* Stars (placeholder - in real app, show earned stars) */}
                {!isLocked && (
                  <div className="flex justify-center gap-1 mb-2">
                    {[1, 2, 3].map((star) => (
                      <Star
                        key={star}
                        className="w-5 h-5"
                        fill="none"
                        stroke="#D0D7E2"
                        strokeWidth={2}
                      />
                    ))}
                  </div>
                )}

                {/* Lock icon */}
                {isLocked && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="bg-gray-800/80 rounded-full p-4">
                      <Lock className="w-8 h-8 text-white" />
                    </div>
                  </div>
                )}

                {/* World indicator */}
                <div className="absolute top-2 left-2 bg-[#4F8BFF] text-white text-xs font-bold px-2 py-1 rounded-full">
                  M{level?.worldNumber ?? 1}
                </div>
              </Link>
            );
          })}
        </div>

        {/* Instructions */}
        <div className="mt-12 bg-white/80 backdrop-blur rounded-3xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-[#1A2130] mb-4">Come Giocare</h2>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-[#00C2A8] font-bold">1.</span>
              <span>Trascina i blocchi colorati sulla griglia</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#00C2A8] font-bold">2.</span>
              <span>Raccogli le monete del colore corrispondente posizionando il blocco sopra</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#00C2A8] font-bold">3.</span>
              <span>Il contatore del blocco diminuisce con ogni moneta raccolta</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#00C2A8] font-bold">4.</span>
              <span>Quando il contatore raggiunge 0, il blocco scompare</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#00C2A8] font-bold">5.</span>
              <span>Completa tutti gli obiettivi prima che scada il tempo!</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
