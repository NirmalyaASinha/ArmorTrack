"use client";

import { ShieldCheck, TrendingUp, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export default function DashboardHome() {
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="card bg-base-100 shadow-xl military-card">
        <div className="card-body">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center">
              <ShieldCheck className="w-8 h-8 text-primary-content" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-base-content uppercase tracking-wider">
                Welcome to ArmorTrack
              </h1>
              <p className="text-base-content/60 mt-1">
                Military-Grade Asset Management & Tracking System
              </p>
            </div>
          </div>
          
          <div className="divider"></div>
          
          <p className="text-base-content/80">
            Select a module from the sidebar to get started. ArmorTrack provides comprehensive 
            asset lifecycle management, real-time GPS tracking, custody chain verification, 
            and audit capabilities.
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-base-100 shadow-xl military-card">
          <div className="card-body">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-base-content/60 uppercase tracking-wider">System Status</p>
                <p className="text-2xl font-bold text-success">Operational</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card bg-base-100 shadow-xl military-card">
          <div className="card-body">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-info/20 rounded-lg flex items-center justify-center">
                <ShieldCheck className="w-6 h-6 text-info" />
              </div>
              <div>
                <p className="text-sm text-base-content/60 uppercase tracking-wider">Security Level</p>
                <p className="text-2xl font-bold text-info">Maximum</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card bg-base-100 shadow-xl military-card">
          <div className="card-body">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-warning/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-warning" />
              </div>
              <div>
                <p className="text-sm text-base-content/60 uppercase tracking-wider">Active Alerts</p>
                <p className="text-2xl font-bold text-warning">0</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="card bg-base-100 shadow-xl military-card">
        <div className="card-body">
          <h2 className="card-title text-xl uppercase tracking-wider mb-4">Quick Access</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Link href="/dashboard/assets" className="btn btn-outline btn-primary military-button">
              Manage Assets
            </Link>
            <Link href="/dashboard/batches" className="btn btn-outline btn-primary military-button">
              View Batches
            </Link>
            <Link href="/dashboard/map" className="btn btn-outline btn-primary military-button">
              Live GPS Map
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
