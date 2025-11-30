
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'TetraCoin - Puzzle Game con Blocchi Tetris',
  description: 'Trascina blocchi a forma di Tetris su una griglia per raccogliere monete del loro colore. Un puzzle game strategico e divertente!',
  icons: {
    icon: '/favicon.svg',
  },
  openGraph: {
    title: 'TetraCoin - Puzzle Game con Blocchi Tetris',
    description: 'Trascina blocchi a forma di Tetris su una griglia per raccogliere monete del loro colore',
    images: ['/og-image.png'],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
