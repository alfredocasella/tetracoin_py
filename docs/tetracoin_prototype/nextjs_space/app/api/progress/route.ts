
export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { levelId, stars, moves, timeRemaining } = body ?? {};

    const userId = 'guest'; // In a real app, get from session/auth

    const progress = await prisma.userProgress.upsert({
      where: {
        userId_levelId: {
          userId,
          levelId: levelId ?? '',
        },
      },
      update: {
        stars: Math.max(stars ?? 0, 0),
        bestMoves: moves ?? undefined,
        bestTime: timeRemaining ?? undefined,
        completed: true,
      },
      create: {
        userId,
        levelId: levelId ?? '',
        stars: stars ?? 0,
        bestMoves: moves ?? undefined,
        bestTime: timeRemaining ?? undefined,
        completed: true,
      },
    });

    return NextResponse.json({ progress });
  } catch (error) {
    console.error('Error saving progress:', error);
    return NextResponse.json({ error: 'Failed to save progress' }, { status: 500 });
  }
}

export async function GET() {
  try {
    const userId = 'guest';

    const progress = await prisma.userProgress.findMany({
      where: { userId },
      include: { level: true },
    });

    return NextResponse.json({ progress });
  } catch (error) {
    console.error('Error fetching progress:', error);
    return NextResponse.json({ error: 'Failed to fetch progress' }, { status: 500 });
  }
}
