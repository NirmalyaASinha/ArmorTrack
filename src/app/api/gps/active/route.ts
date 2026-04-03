import { NextResponse } from 'next/server';

// Mock GPS data
const mockGPSData = [
  {
    id: 'gps-1',
    batchId: 'BATCH-001',
    transporterName: 'Transport Unit Alpha',
    assetsCount: 15,
    lat: 28.6139,
    lng: 77.209,
    lastUpdated: new Date().toISOString(),
    alert: false,
  },
  {
    id: 'gps-2',
    batchId: 'BATCH-002',
    transporterName: 'Transport Unit Bravo',
    assetsCount: 8,
    lat: 19.076,
    lng: 72.8777,
    lastUpdated: new Date().toISOString(),
    alert: true,
  },
  {
    id: 'gps-3',
    batchId: 'BATCH-003',
    transporterName: 'Transport Unit Charlie',
    assetsCount: 22,
    lat: 12.9716,
    lng: 77.5946,
    lastUpdated: new Date().toISOString(),
    alert: false,
  },
];

export async function GET() {
  try {
    // Add slight random movement to simulate real GPS
    const updatedData = mockGPSData.map(batch => ({
      ...batch,
      lat: batch.lat + (Math.random() - 0.5) * 0.01,
      lng: batch.lng + (Math.random() - 0.5) * 0.01,
      lastUpdated: new Date().toISOString(),
    }));

    return NextResponse.json({ batches: updatedData });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch GPS data' },
      { status: 500 }
    );
  }
}
