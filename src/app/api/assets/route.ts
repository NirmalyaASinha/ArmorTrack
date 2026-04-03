import { NextRequest, NextResponse } from 'next/server';
import { Asset } from '@/types/asset';

// Mock data
const mockAssets: Asset[] = [
  {
    id: 'AST-001',
    name: 'M4 Carbine Rifle',
    type: 'Weapon System',
    status: 'WAREHOUSE',
    currentCustodian: 'Warehouse A',
    lastUpdated: new Date().toISOString(),
  },
  {
    id: 'AST-002',
    name: 'Humvee H1',
    type: 'Vehicle',
    status: 'IN_TRANSIT',
    currentCustodian: 'Transport Unit 5',
    lastUpdated: new Date().toISOString(),
  },
  {
    id: 'AST-003',
    name: 'Radio Set AN/PRC-152',
    type: 'Communication Device',
    status: 'DEPLOYED',
    currentCustodian: 'Field Unit Alpha',
    lastUpdated: new Date().toISOString(),
  },
  {
    id: 'AST-004',
    name: 'Night Vision Goggles',
    type: 'Surveillance Equipment',
    status: 'WAREHOUSE',
    currentCustodian: 'Warehouse B',
    lastUpdated: new Date().toISOString(),
  },
  {
    id: 'AST-005',
    name: 'Body Armor Plate Carrier',
    type: 'Protective Gear',
    status: 'MAINTENANCE_DUE',
    currentCustodian: 'Maintenance Bay 2',
    lastUpdated: new Date().toISOString(),
  },
];

export async function GET(request: NextRequest) {
  try {
    // Get query params for filtering
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    
    let assets = mockAssets;
    if (status) {
      assets = assets.filter(a => a.status === status);
    }
    
    return NextResponse.json({ assets });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch assets' },
      { status: 500 }
    );
  }
}
