import { NextResponse } from 'next/server';
import { Batch } from '@/types/batch';

const mockBatches: Batch[] = [
  {
    id: 'BATCH-001',
    assetsCount: 15,
    transporter: 'Transport Unit Alpha',
    status: 'IN_TRANSIT',
    destination: 'Forward Base Delta',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 'BATCH-002',
    assetsCount: 8,
    transporter: 'Transport Unit Bravo',
    status: 'PENDING',
    destination: 'Warehouse Complex B',
    createdAt: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'BATCH-003',
    assetsCount: 22,
    transporter: 'Transport Unit Charlie',
    status: 'DELIVERED',
    destination: 'Command Center',
    createdAt: new Date(Date.now() - 172800000).toISOString(),
  },
];

export async function GET() {
  try {
    return NextResponse.json({ batches: mockBatches });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch batches' },
      { status: 500 }
    );
  }
}
