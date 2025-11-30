
export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET() {
  try {
    const levels = await prisma.level.findMany({
      orderBy: [{ worldNumber: 'asc' }, { levelNumber: 'asc' }],
    });

    return NextResponse.json({ levels });
  } catch (error) {
    console.error('Error fetching levels:', error);
    return NextResponse.json({ error: 'Failed to fetch levels' }, { status: 500 });
  }
}
