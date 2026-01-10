/**
 * EOS Platform - Client Portal Campaigns
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { portalApi } from '@/services/api';
import type { Campaign, CampaignStatus } from '@/types';
import {
  MagnifyingGlassIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

// Format currency from micros
const formatCurrency = (micros: number, currency = 'EUR') => {
  const amount = micros / 1_000_000;
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

// Format date
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

// Status badge colors
const statusColors: Record<CampaignStatus, string> = {
  draft: 'badge-secondary',
  pending_approval: 'badge-warning',
  approved: 'badge-info',
  active: 'badge-success',
  paused: 'badge-warning',
  completed: 'badge-primary',
  cancelled: 'badge-danger',
};

// Campaign Card Component
function CampaignCard({ campaign }: { campaign: Campaign }) {
  const [expanded, setExpanded] = useState(false);
  const budgetUtilization = campaign.budget_micros > 0
    ? (campaign.spent_micros / campaign.budget_micros) * 100
    : 0;

  return (
    <div className="card overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
            <p className="text-sm text-gray-500">{campaign.code}</p>
          </div>
          <span className={`badge ${statusColors[campaign.status]}`}>
            {campaign.status.replace('_', ' ')}
          </span>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="flex items-center">
            <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-sm">
              <p className="text-gray-500">Duration</p>
              <p className="text-gray-900">
                {formatDate(campaign.start_date)} - {formatDate(campaign.end_date)}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-sm">
              <p className="text-gray-500">Budget</p>
              <p className="text-gray-900 font-medium">
                {formatCurrency(campaign.budget_micros, campaign.currency)}
              </p>
            </div>
          </div>
        </div>

        {/* Budget utilization */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-500">Budget Utilization</span>
            <span className={`font-medium ${
              budgetUtilization > 90 ? 'text-red-600' : 'text-gray-900'
            }`}>
              {budgetUtilization.toFixed(1)}%
            </span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                budgetUtilization > 90
                  ? 'bg-red-500'
                  : budgetUtilization > 70
                  ? 'bg-yellow-500'
                  : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(budgetUtilization, 100)}%` }}
            />
          </div>
        </div>

        {campaign.objective && (
          <div className="mt-4">
            <p className="text-sm text-gray-500">Objective</p>
            <p className="text-sm text-gray-900">{campaign.objective}</p>
          </div>
        )}

        {/* Expandable details */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-4 text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          {expanded ? 'Show less' : 'Show more'}
        </button>

        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Campaign Type</p>
                <p className="text-gray-900 capitalize">{campaign.campaign_type}</p>
              </div>
              <div>
                <p className="text-gray-500">Media Plans</p>
                <p className="text-gray-900">{campaign.media_plans_count || 0}</p>
              </div>
            </div>
            {campaign.target_audience && (
              <div className="text-sm">
                <p className="text-gray-500">Target Audience</p>
                <p className="text-gray-900">{campaign.target_audience}</p>
              </div>
            )}
            {campaign.description && (
              <div className="text-sm">
                <p className="text-gray-500">Description</p>
                <p className="text-gray-900">{campaign.description}</p>
              </div>
            )}
            <div className="text-sm">
              <p className="text-gray-500">Spent</p>
              <p className="text-gray-900 font-medium">
                {formatCurrency(campaign.spent_micros, campaign.currency)}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function PortalCampaigns() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<CampaignStatus | ''>('');

  // Fetch campaigns
  const { data: campaignsData, isLoading } = useQuery({
    queryKey: ['portal-campaigns'],
    queryFn: portalApi.getCampaigns,
  });

  const campaigns = campaignsData?.results || [];

  // Filter campaigns
  const filteredCampaigns = campaigns.filter((campaign: Campaign) => {
    const matchesSearch = searchTerm === '' ||
      campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      campaign.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || campaign.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Calculate summary stats
  const activeCampaigns = campaigns.filter((c: Campaign) => c.status === 'active').length;
  const totalBudget = campaigns.reduce((sum: number, c: Campaign) => sum + c.budget_micros, 0);
  const totalSpent = campaigns.reduce((sum: number, c: Campaign) => sum + c.spent_micros, 0);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Campaigns</h1>
        <p className="mt-1 text-sm text-gray-500">View and track your advertising campaigns</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-50 rounded-lg">
              <ChartBarIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-lg font-bold text-gray-900">{activeCampaigns}</p>
              <p className="text-sm text-gray-500">Active Campaigns</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-50 rounded-lg">
              <CurrencyDollarIcon className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-lg font-bold text-gray-900">{formatCurrency(totalBudget)}</p>
              <p className="text-sm text-gray-500">Total Budget</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-50 rounded-lg">
              <CurrencyDollarIcon className="h-5 w-5 text-purple-600" />
            </div>
            <div className="ml-3">
              <p className="text-lg font-bold text-gray-900">{formatCurrency(totalSpent)}</p>
              <p className="text-sm text-gray-500">Total Spent</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search campaigns..."
              className="input pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as CampaignStatus | '')}
            className="input w-40"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="pending_approval">Pending</option>
            <option value="completed">Completed</option>
            <option value="paused">Paused</option>
          </select>
        </div>
      </div>

      {/* Campaigns grid */}
      {filteredCampaigns.length === 0 ? (
        <div className="card text-center py-12">
          <ChartBarIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p className="text-gray-500">No campaigns found</p>
          {searchTerm || statusFilter ? (
            <button
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('');
              }}
              className="mt-4 text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Clear filters
            </button>
          ) : null}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCampaigns.map((campaign: Campaign) => (
            <CampaignCard key={campaign.id} campaign={campaign} />
          ))}
        </div>
      )}
    </div>
  );
}
