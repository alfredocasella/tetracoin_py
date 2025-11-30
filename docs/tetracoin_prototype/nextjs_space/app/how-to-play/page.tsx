
import Link from 'next/link';
import { ArrowLeft, Move, Target, Timer, Trophy } from 'lucide-react';

export default function HowToPlayPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#F2F7FF] to-[#DCE7F9] py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Link
            href="/"
            className="flex items-center gap-2 text-[#1A2130] font-bold text-lg hover:text-[#00C2A8] transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
            Menu Principale
          </Link>
        </div>

        <h1 className="text-5xl font-bold text-[#1A2130] mb-8 text-center">Come si Gioca</h1>

        {/* Game Concept */}
        <div className="bg-white rounded-3xl p-8 shadow-lg mb-6">
          <h2 className="text-3xl font-bold text-[#00C2A8] mb-4">Il Concetto</h2>
          <p className="text-lg text-gray-700 leading-relaxed">
            TetraCoin è un puzzle game dove trascini blocchi a forma di Tetris su una griglia per
            raccogliere monete colorate. Ogni blocco ha un contatore che diminuisce quando raccogli
            monete del suo colore. L'obiettivo è far scomparire tutti i blocchi e raccogliere tutte
            le monete prima che scada il tempo!
          </p>
        </div>

        {/* Core Mechanics */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="bg-[#00C2A8] rounded-full p-3 mt-1">
                <Move className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#1A2130] mb-2">Trascina i Blocchi</h3>
                <p className="text-gray-700">
                  Tocca e trascina un blocco sulla griglia. Il blocco si aggancerà automaticamente
                  alla posizione più vicina. Puoi muovere i blocchi liberamente, ma non possono
                  sovrapporsi con muri o altri blocchi.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="bg-[#FFD66B] rounded-full p-3 mt-1">
                <Target className="w-8 h-8 text-[#D9A842]" />
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#1A2130] mb-2">Raccogli Monete</h3>
                <p className="text-gray-700">
                  Quando posizioni un blocco su monete del suo colore, le monete vengono
                  automaticamente raccolte. Il contatore sul blocco diminuisce di 1 per ogni moneta
                  raccolta. Pianifica bene i tuoi movimenti per raccogliere più monete possibile
                  con un singolo movimento!
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="bg-[#B870FF] rounded-full p-3 mt-1">
                <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center text-[#B870FF] font-bold text-xl">
                  0
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#1A2130] mb-2">Contatori e Scomparsa</h3>
                <p className="text-gray-700">
                  Ogni blocco ha un numero al centro che indica quante monete deve ancora
                  raccogliere. Quando il contatore raggiunge 0, il blocco scompare immediatamente,
                  liberando spazio sulla griglia per altri movimenti.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="bg-[#FF9F43] rounded-full p-3 mt-1">
                <Timer className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#1A2130] mb-2">Timer e Stati</h3>
                <p className="text-gray-700 mb-3">
                  Ogni livello ha un limite di tempo. Il timer cambia colore per avvisarti:
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[#4F8BFF]" />
                    <span className="text-gray-700">
                      <strong>Blu:</strong> Tempo normale, tutto ok
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[#FF9F43]" />
                    <span className="text-gray-700">
                      <strong>Arancione:</strong> Attenzione, meno del 50% di tempo
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[#FF5A5A]" />
                    <span className="text-gray-700">
                      <strong>Rosso:</strong> Critico! Meno del 20% di tempo
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="bg-[#33CC7A] rounded-full p-3 mt-1">
                <Trophy className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#1A2130] mb-2">Vittoria e Stelle</h3>
                <p className="text-gray-700 mb-3">
                  Per vincere un livello devi:
                </p>
                <ul className="list-disc list-inside space-y-1 text-gray-700 mb-3">
                  <li>Far scomparire tutti i blocchi (contatore a 0)</li>
                  <li>Raccogliere tutte le monete</li>
                  <li>Completare prima che scada il tempo</li>
                </ul>
                <p className="text-gray-700">
                  Guadagni fino a 3 stelle in base al numero di mosse utilizzate. Meno mosse = più
                  stelle!
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="bg-gradient-to-r from-[#00C2A8] to-[#4F8BFF] rounded-3xl p-8 shadow-lg mt-8 text-white">
          <h2 className="text-3xl font-bold mb-4">Suggerimenti Strategici</h2>
          <ul className="space-y-3 text-lg">
            <li className="flex items-start gap-2">
              <span className="font-bold">💡</span>
              <span>Pianifica i movimenti: pensa a come raccogliere più monete con meno mosse</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">💡</span>
              <span>
                Priorità ai blocchi: a volte devi muovere un blocco per liberare spazio per un altro
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">💡</span>
              <span>Usa il pulsante Reset se rimani bloccato - non c'è penalità!</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">💡</span>
              <span>Tieni d'occhio il timer - pianifica prima, muovi dopo</span>
            </li>
          </ul>
        </div>

        {/* CTA */}
        <div className="text-center mt-8">
          <Link href="/levels">
            <button className="px-12 py-5 bg-[#00C2A8] hover:bg-[#00A690] text-white font-bold text-2xl rounded-full shadow-2xl transition-all duration-200 hover:scale-105">
              Inizia a Giocare!
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
