"use client";

import { useState, useEffect } from 'react';
import { Search, Plus } from 'lucide-react';
import { Asset } from '@/types/asset';
import { getToken } from '@/lib/auth';
import StatusBadge from '@/components/assets/StatusBadge';
import RegisterAssetModal from '@/components/assets/RegisterAssetModal';

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchAssets = async () => {
    try {
      const token = getToken();
      const response = await fetch('/api/assets', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setAssets(Array.isArray(data.assets) ? data.assets : []);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
      setAssets([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  // Filter assets based on search query
  const filteredAssets = assets.filter(
    (asset) =>
      (asset.id || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (asset.name || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const openModal = () => {
    const modal = document.getElementById('register_asset_modal') as HTMLDialogElement;
    if (modal) modal.showModal();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <span className="loading loading-spinner loading-lg text-primary"></span>
          <p className="text-base-content/70 uppercase tracking-wider">Loading assets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-base-content uppercase tracking-wider">
            Asset Management
          </h1>
          <p className="text-base-content/60 mt-1">
            Track and manage all military assets
          </p>
        </div>
        <button onClick={openModal} className="btn btn-primary military-button">
          <Plus className="w-5 h-5" />
          Register Asset
        </button>
      </div>

      {/* Search Bar */}
      <div className="card bg-base-100 shadow-xl military-card">
        <div className="card-body p-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-base-content/40" />
            <input
              type="text"
              placeholder="Search by Asset ID or Name..."
              className="input input-bordered w-full max-w-2xl pl-12 military-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Assets Table */}
      <div className="card bg-base-100 shadow-xl military-card">
        <div className="card-body p-0">
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              {/* Header */}
              <thead>
                <tr className="bg-base-200">
                  <th className="uppercase tracking-wider text-sm">Asset ID</th>
                  <th className="uppercase tracking-wider text-sm">Name</th>
                  <th className="uppercase tracking-wider text-sm">Type</th>
                  <th className="uppercase tracking-wider text-sm">Status</th>
                  <th className="uppercase tracking-wider text-sm">Current Custodian</th>
                  <th className="uppercase tracking-wider text-sm">Last Updated</th>
                </tr>
              </thead>
              
              {/* Body */}
              <tbody>
                {filteredAssets.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-base-content/60">
                      No assets found
                    </td>
                  </tr>
                ) : (
                  filteredAssets.map((asset) => (
                    <tr key={asset.id} className="hover:bg-base-200/50">
                      <td className="font-mono font-bold text-primary">{asset.id}</td>
                      <td className="font-semibold">{asset.name}</td>
                      <td>{asset.type}</td>
                      <td>
                        <StatusBadge status={asset.status} />
                      </td>
                      <td>{asset.currentCustodian}</td>
                      <td className="text-base-content/70">
                        {new Date(asset.lastUpdated).toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Register Asset Modal */}
      <RegisterAssetModal onAssetRegistered={fetchAssets} />
    </div>
  );
}
