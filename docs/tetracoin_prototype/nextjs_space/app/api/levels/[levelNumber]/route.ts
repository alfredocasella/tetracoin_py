
export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: { levelNumber: string } }
) {
  try {
    const levelNumber = parseInt(params?.levelNumber ?? '1', 10);

    const level = await prisma.level.findUnique({
      where: { levelNumber },
    });

    if (!level) {
      return NextResponse.json({ error: 'Level not found' }, { status: 404 });
    }

    return NextResponse.json({ level });
  } catch (error) {
    console.error('Error fetching level:', error);
    return NextResponse.json({ error: 'Failed to fetch level' }, { status: 500 });
  }
}
