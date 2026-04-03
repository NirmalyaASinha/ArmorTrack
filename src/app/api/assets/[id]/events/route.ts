import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params;
    
    // Mock custody events
    const mockEvents = [
      {
        id: 'evt-1',
        type: 'REGISTERED',
        timestamp: new Date(Date.now() - 604800000).toISOString(),
        personResponsible: 'Warehouse Admin',
        location: { lat: 28.6139, lng: 77.209 },
      },
      {
        id: 'evt-2',
        type: 'CHECKED_OUT',
        timestamp: new Date(Date.now() - 432000000).toISOString(),
        personResponsible: 'Sgt. Johnson',
        location: { lat: 28.6200, lng: 77.2150 },
      },
      {
        id: 'evt-3',
        type: 'DISPATCHED',
        timestamp: new Date(Date.now() - 259200000).toISOString(),
        personResponsible: 'Transport Unit Alpha',
        location: { lat: 28.6500, lng: 77.2300 },
      },
      {
        id: 'evt-4',
        type: 'IN_TRANSIT',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        personResponsible: 'Transport Unit Alpha',
      },
      {
        id: 'evt-5',
        type: 'DELIVERED',
        timestamp: new Date().toISOString(),
        personResponsible: 'Field Unit Commander',
        location: { lat: 28.7000, lng: 77.3000 },
      },
    ];

    return NextResponse.json({ events: mockEvents });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch custody events' },
      { status: 500 }
    );
  }
}
