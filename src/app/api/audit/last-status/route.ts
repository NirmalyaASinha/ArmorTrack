import { NextResponse } from 'next/server';

export async function GET() {
  try {
    return NextResponse.json({ status: 'OK', lastRun: new Date().toISOString() });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch audit status' },
      { status: 500 }
    );
  }
}
