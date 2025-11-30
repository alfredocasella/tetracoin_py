
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Play, Trophy, Info } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#F2F7FF] via-[#DCE7F9] to-[#00C2A8]/20 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        {/* Logo/Title */}
        <div className="mb-8">
          <h1 className="text-6xl md:text-7xl font-bold text-[#1A2130] mb-4 tracking-tight">
            Tetra<span className="text-[#00C2A8]">Coin</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 font-medium">
            Trascina i blocchi, raccogli le monete!
          </p>
        </div>

        {/* Decorative blocks */}
        <div className="flex justify-center gap-4 mb-12">
          <div className="w-16 h-16 rounded-lg bg-[#FFC94D] border-4 border-[#D9981F] shadow-lg animate-bounce" 
               style={{ animationDelay: '0s' }} />
          <div className="w-16 h-16 rounded-lg bg-[#4F8BFF] border-4 border-[#2A57BF] shadow-lg animate-bounce" 
               style={{ animationDelay: '0.1s' }} />
          <div className="w-16 h-16 rounded-lg bg-[#FF5A5A] border-4 border-[#C23030] shadow-lg animate-bounce" 
               style={{ animationDelay: '0.2s' }} />
          <div className="w-16 h-16 rounded-lg bg-[#33CC7A] border-4 border-[#229957] shadow-lg animate-bounce" 
               style={{ animationDelay: '0.3s' }} />
        </div>

        {/* Main Menu Buttons */}
        <div className="space-y-4">
          <Link href="/levels">
            <button className="w-full py-6 bg-[#00C2A8] hover:bg-[#00A690] text-white font-bold text-2xl rounded-full shadow-2xl transition-all duration-200 hover:scale-105 flex items-center justify-center gap-3">
              <Play className="w-8 h-8" fill="white" />
              Gioca
            </button>
          </Link>

          <Link href="/how-to-play">
            <button className="w-full py-5 bg-white hover:bg-gray-50 border-4 border-[#4F8BFF] text-[#4F8BFF] font-bold text-xl rounded-full shadow-lg transition-all duration-200 hover:scale-105 flex items-center justify-center gap-3">
              <Info className="w-7 h-7" />
              Come si Gioca
            </button>
          </Link>
        </div>

        {/* Feature highlights */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-md">
            <Trophy className="w-8 h-8 mx-auto mb-2 text-[#FFD66B]" />
            <p className="font-bold text-[#1A2130]">10 Livelli</p>
            <p className="text-gray-600">Progressione sfidante</p>
          </div>
          <div className="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-md">
            <div className="w-8 h-8 mx-auto mb-2 bg-[#4F8BFF] rounded-lg" />
            <p className="font-bold text-[#1A2130]">Forme Tetris</p>
            <p className="text-gray-600">7 blocchi unici</p>
          </div>
          <div className="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-md">
            <div className="flex justify-center gap-1 mb-2">
              <div className="w-3 h-3 rounded-full bg-[#FFC94D]" />
              <div className="w-3 h-3 rounded-full bg-[#4F8BFF]" />
              <div className="w-3 h-3 rounded-full bg-[#FF5A5A]" />
              <div className="w-3 h-3 rounded-full bg-[#33CC7A]" />
              <div className="w-3 h-3 rounded-full bg-[#B870FF]" />
            </div>
            <p className="font-bold text-[#1A2130]">5 Colori</p>
            <p className="text-gray-600">Puzzle strategici</p>
          </div>
        </div>
      </div>
    </div>
  );
}
