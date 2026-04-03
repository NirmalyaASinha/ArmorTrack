export interface Asset {
  id: string;
  name: string;
  type: string;
  status: 'WAREHOUSE' | 'IN_TRANSIT' | 'DEPLOYED' | 'MAINTENANCE_DUE';
  currentCustodian: string;
  lastUpdated: string;
}

export interface RegisterAssetInput {
  name: string;
  type: string;
}
