/**
 * EOS Platform - Media Plans Page
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { mediaPlansApi, campaignsApi } from '@/services/api';
import type { MediaPlan, MediaPlanFilters, MediaPlanStatus, Campaign } from '@/types';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  EllipsisVerticalIcon,
  DocumentDuplicateIcon,
  TrashIcon,
  PencilIcon,
  CheckCircleIcon,
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
const statusColors: Record<MediaPlanStatus, string> = {
  draft: 'badge-secondary',
  pending_approval: 'badge-warning',
  approved: 'badge-success',
  active: 'badge-primary',
  completed: 'badge-info',
};

// Create Media Plan Modal
interface CreateMediaPlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  campaigns: Campaign[];
  defaultCampaignId?: number;
}

function CreateMediaPlanModal({ isOpen, onClose, campaigns, defaultCampaignId }: CreateMediaPlanModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    campaign: defaultCampaignId?.toString() || '',
    name: '',
    code: '',
    description: '',
    start_date: '',
    end_date: '',
    total_budget_micros: '',
    currency: 'EUR',
  });

  const createMutation = useMutation({
    mutationFn: mediaPlansApi.createMediaPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plans'] });
      onClose();
      setFormData({
        campaign: '',
        name: '',
        code: '',
        description: '',
        start_date: '',
        end_date: '',
        total_budget_micros: '',
        currency: 'EUR',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      campaign: parseInt(formData.campaign),
      name: formData.name,
      code: formData.code,
      description: formData.description || undefined,
      start_date: formData.start_date,
      end_date: formData.end_date,
      total_budget_micros: Math.round(parseFloat(formData.total_budget_micros) * 1_000_000),
      currency: formData.currency,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6 text-left">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Media Plan</h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Campaign</label>
              <select
                value={formData.campaign}
                onChange={(e) => setFormData({ ...formData, campaign: e.target.value })}
                required
                className="input"
              >
                <option value="">Select campaign</option>
                {campaigns.map((camp) => (
                  <option key={camp.id} value={camp.id}>
                    {camp.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="input"
                  placeholder="Media Plan Q1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Code</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  required
                  className="input"
                  placeholder="MP-001"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="input"
                placeholder="Media plan description..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  required
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  required
                  className="input"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Budget</label>
                <input
                  type="number"
                  value={formData.total_budget_micros}
                  onChange={(e) => setFormData({ ...formData, total_budget_micros: e.target.value })}
                  required
                  min="0"
                  step="0.01"
                  className="input"
                  placeholder="5000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
                <select
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="input"
                >
                  <option value="EUR">EUR</option>
                  <option value="USD">USD</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button type="button" onClick={onClose} className="btn btn-secondary">
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="btn btn-primary"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Media Plan'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function MediaPlansPage() {
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<MediaPlanFilters>({
    campaign: searchParams.get('campaign') ? parseInt(searchParams.get('campaign')!) : undefined,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  // Fetch media plans
  const { data: mediaPlansData, isLoading } = useQuery({
    queryKey: ['media-plans', filters],
    queryFn: () => mediaPlansApi.getMediaPlans({ ...filters, search: searchTerm || undefined }),
  });

  // Fetch campaigns for create modal
  const { data: campaignsData } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.getCampaigns(),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: mediaPlansApi.deleteMediaPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plans'] });
    },
  });

  // Duplicate mutation
  const duplicateMutation = useMutation({
    mutationFn: mediaPlansApi.duplicateMediaPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plans'] });
    },
  });

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: (id: number) => mediaPlansApi.approveMediaPlan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plans'] });
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search: searchTerm });
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this media plan?')) {
      deleteMutation.mutate(id);
    }
    setOpenMenuId(null);
  };

  const handleDuplicate = (id: number) => {
    duplicateMutation.mutate(id);
    setOpenMenuId(null);
  };

  const handleApprove = (id: number) => {
    approveMutation.mutate(id);
    setOpenMenuId(null);
  };

  const mediaPlans = mediaPlansData?.results || [];
  const campaigns = campaignsData?.results || [];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Media Plans</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your media planning documents</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
            <PlusIcon className="h-5 w-5 mr-2" />
            New Media Plan
          </button>
        </div>
      </div>

      {/* Search and filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search media plans..."
                className="input pl-10"
              />
            </div>
          </form>

          <div className="flex gap-2">
            <select
              value={filters.status || ''}
              onChange={(e) =>
                setFilters({ ...filters, status: (e.target.value as MediaPlanStatus) || undefined })
              }
              className="input w-40"
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="pending_approval">Pending</option>
              <option value="approved">Approved</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>

            <select
              value={filters.campaign || ''}
              onChange={(e) =>
                setFilters({ ...filters, campaign: e.target.value ? parseInt(e.target.value) : undefined })
              }
              className="input w-48"
            >
              <option value="">All Campaigns</option>
              {campaigns.map((camp: Campaign) => (
                <option key={camp.id} value={camp.id}>
                  {camp.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Media Plans grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : mediaPlans.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No media plans found</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary mt-4"
          >
            Create your first media plan
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mediaPlans.map((mediaPlan: MediaPlan) => (
            <div key={mediaPlan.id} className="card p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <Link
                    to={`/media-plans/${mediaPlan.id}`}
                    className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                  >
                    {mediaPlan.name}
                  </Link>
                  <p className="text-sm text-gray-500">{mediaPlan.code}</p>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setOpenMenuId(openMenuId === mediaPlan.id ? null : mediaPlan.id)}
                    className="p-1 hover:bg-gray-100 rounded-lg"
                  >
                    <EllipsisVerticalIcon className="h-5 w-5 text-gray-500" />
                  </button>

                  {openMenuId === mediaPlan.id && (
                    <>
                      <div
                        className="fixed inset-0 z-40"
                        onClick={() => setOpenMenuId(null)}
                      />
                      <div className="absolute right-0 z-50 mt-2 w-48 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5">
                        <div className="py-1">
                          <Link
                            to={`/media-plans/${mediaPlan.id}`}
                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            onClick={() => setOpenMenuId(null)}
                          >
                            <PencilIcon className="h-4 w-4 mr-3" />
                            Edit
                          </Link>
                          {mediaPlan.status === 'pending_approval' && (
                            <button
                              onClick={() => handleApprove(mediaPlan.id)}
                              className="flex items-center w-full px-4 py-2 text-sm text-green-600 hover:bg-gray-100"
                            >
                              <CheckCircleIcon className="h-4 w-4 mr-3" />
                              Approve
                            </button>
                          )}
                          <button
                            onClick={() => handleDuplicate(mediaPlan.id)}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <DocumentDuplicateIcon className="h-4 w-4 mr-3" />
                            Duplicate
                          </button>
                          <hr className="my-1" />
                          <button
                            onClick={() => handleDelete(mediaPlan.id)}
                            className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                          >
                            <TrashIcon className="h-4 w-4 mr-3" />
                            Delete
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="mt-4">
                <p className="text-sm text-gray-500">Campaign</p>
                <p className="text-gray-900">{mediaPlan.campaign_name || '-'}</p>
              </div>

              <div className="mt-4 flex items-center justify-between">
                <span className={`badge ${statusColors[mediaPlan.status]}`}>
                  {mediaPlan.status.replace('_', ' ')}
                </span>
                <span className="text-sm text-gray-500">v{mediaPlan.version}</span>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Budget</span>
                  <span className="font-semibold text-gray-900">
                    {formatCurrency(mediaPlan.total_budget_micros, mediaPlan.currency)}
                  </span>
                </div>
                <div className="flex justify-between text-sm mt-2">
                  <span className="text-gray-500">Period</span>
                  <span className="text-gray-700">
                    {formatDate(mediaPlan.start_date)} - {formatDate(mediaPlan.end_date)}
                  </span>
                </div>
                <div className="flex justify-between text-sm mt-2">
                  <span className="text-gray-500">Subcampaigns</span>
                  <span className="text-gray-700">{mediaPlan.subcampaigns_count || 0}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination info */}
      {mediaPlansData && mediaPlansData.count > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Showing {mediaPlans.length} of {mediaPlansData.count} media plans
          </p>
        </div>
      )}

      {/* Create Media Plan Modal */}
      <CreateMediaPlanModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        campaigns={campaigns}
        defaultCampaignId={filters.campaign}
      />
    </div>
  );
}
