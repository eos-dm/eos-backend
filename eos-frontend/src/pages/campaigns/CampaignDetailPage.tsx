/**
 * EOS Platform - Campaign Detail Page
 */
import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignsApi, mediaPlansApi } from '@/services/api';
import type { Campaign, MediaPlan } from '@/types';
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  DocumentChartBarIcon,
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
    month: 'long',
    day: 'numeric',
  });
};

// Status badge colors
const statusColors: Record<string, string> = {
  draft: 'badge-secondary',
  pending_approval: 'badge-warning',
  approved: 'badge-info',
  active: 'badge-success',
  paused: 'badge-warning',
  completed: 'badge-primary',
  cancelled: 'badge-danger',
};

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Campaign>>({});

  // Fetch campaign
  const { data: campaign, isLoading: isLoadingCampaign } = useQuery({
    queryKey: ['campaign', id],
    queryFn: () => campaignsApi.getCampaign(parseInt(id!)),
    enabled: !!id,
  });

  // Fetch media plans
  const { data: mediaPlansData, isLoading: isLoadingMediaPlans } = useQuery({
    queryKey: ['media-plans', { campaign: id }],
    queryFn: () => mediaPlansApi.getMediaPlans({ campaign: parseInt(id!) }),
    enabled: !!id,
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: Partial<Campaign>) => campaignsApi.updateCampaign(parseInt(id!), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaign', id] });
      setIsEditing(false);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => campaignsApi.deleteCampaign(parseInt(id!)),
    onSuccess: () => {
      navigate('/campaigns');
    },
  });

  // Status change mutation
  const statusMutation = useMutation({
    mutationFn: (status: string) => campaignsApi.changeCampaignStatus(parseInt(id!), status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaign', id] });
    },
  });

  const handleEdit = () => {
    if (campaign) {
      setEditForm({
        name: campaign.name,
        code: campaign.code,
        description: campaign.description,
        objective: campaign.objective,
        start_date: campaign.start_date,
        end_date: campaign.end_date,
        target_audience: campaign.target_audience,
      });
      setIsEditing(true);
    }
  };

  const handleSave = () => {
    updateMutation.mutate(editForm);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this campaign?')) {
      deleteMutation.mutate();
    }
  };

  const handleStatusChange = (newStatus: string) => {
    statusMutation.mutate(newStatus);
  };

  if (isLoadingCampaign) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Campaign not found</p>
        <Link to="/campaigns" className="btn btn-primary mt-4">
          Back to Campaigns
        </Link>
      </div>
    );
  }

  const mediaPlans = mediaPlansData?.results || [];
  const totalMediaPlanBudget = mediaPlans.reduce((sum: number, mp: MediaPlan) => sum + mp.total_budget_micros, 0);
  const budgetUtilization = campaign.budget_micros > 0
    ? (campaign.spent_micros / campaign.budget_micros) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Back button and header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center">
          <Link
            to="/campaigns"
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{campaign.name}</h1>
            <p className="mt-1 text-sm text-gray-500">{campaign.code}</p>
          </div>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <span className={`badge ${statusColors[campaign.status]}`}>
            {campaign.status.replace('_', ' ')}
          </span>
          <button onClick={handleEdit} className="btn btn-secondary">
            <PencilIcon className="h-4 w-4 mr-2" />
            Edit
          </button>
          <button onClick={handleDelete} className="btn btn-danger">
            <TrashIcon className="h-4 w-4 mr-2" />
            Delete
          </button>
        </div>
      </div>

      {/* Campaign details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main info */}
        <div className="lg:col-span-2 card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Details</h3>

          {isEditing ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={editForm.name || ''}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Code</label>
                  <input
                    type="text"
                    value={editForm.code || ''}
                    onChange={(e) => setEditForm({ ...editForm, code: e.target.value })}
                    className="input"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Objective</label>
                <input
                  type="text"
                  value={editForm.objective || ''}
                  onChange={(e) => setEditForm({ ...editForm, objective: e.target.value })}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={editForm.description || ''}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={3}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
                <input
                  type="text"
                  value={editForm.target_audience || ''}
                  onChange={(e) => setEditForm({ ...editForm, target_audience: e.target.value })}
                  className="input"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={editForm.start_date || ''}
                    onChange={(e) => setEditForm({ ...editForm, start_date: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={editForm.end_date || ''}
                    onChange={(e) => setEditForm({ ...editForm, end_date: e.target.value })}
                    className="input"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <button onClick={() => setIsEditing(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button onClick={handleSave} className="btn btn-primary">
                  Save Changes
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Project</p>
                  <Link
                    to={`/projects/${campaign.project}`}
                    className="text-primary-600 hover:text-primary-800"
                  >
                    {campaign.project_name || '-'}
                  </Link>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Type</p>
                  <p className="text-gray-900 capitalize">{campaign.campaign_type}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Objective</p>
                <p className="text-gray-900">{campaign.objective || 'No objective defined'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Description</p>
                <p className="text-gray-900">{campaign.description || 'No description'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Target Audience</p>
                <p className="text-gray-900">{campaign.target_audience || 'Not specified'}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center">
                  <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm text-gray-500">Start Date</p>
                    <p className="text-gray-900">{formatDate(campaign.start_date)}</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm text-gray-500">End Date</p>
                    <p className="text-gray-900">{formatDate(campaign.end_date)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Budget and performance */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Budget & Performance</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-green-500 mr-2" />
                <span className="text-sm text-gray-500">Total Budget</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(campaign.budget_micros, campaign.currency)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <ChartBarIcon className="h-5 w-5 text-blue-500 mr-2" />
                <span className="text-sm text-gray-500">Spent</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(campaign.spent_micros, campaign.currency)}
              </span>
            </div>

            {/* Budget utilization bar */}
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-500">Utilization</span>
                <span className="font-medium">{budgetUtilization.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    budgetUtilization > 90 ? 'bg-red-500' : budgetUtilization > 70 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(budgetUtilization, 100)}%` }}
                />
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <DocumentChartBarIcon className="h-5 w-5 text-purple-500 mr-2" />
                  <span className="text-sm text-gray-500">Media Plans Budget</span>
                </div>
                <span className="text-lg font-semibold text-gray-900">
                  {formatCurrency(totalMediaPlanBudget, campaign.currency)}
                </span>
              </div>
            </div>

            {/* Status actions */}
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-2">Change Status</p>
              <div className="flex flex-wrap gap-2">
                {campaign.status === 'draft' && (
                  <button
                    onClick={() => handleStatusChange('pending_approval')}
                    className="btn btn-sm btn-warning"
                  >
                    Submit for Approval
                  </button>
                )}
                {campaign.status === 'pending_approval' && (
                  <button
                    onClick={() => handleStatusChange('approved')}
                    className="btn btn-sm btn-success"
                  >
                    Approve
                  </button>
                )}
                {campaign.status === 'approved' && (
                  <button
                    onClick={() => handleStatusChange('active')}
                    className="btn btn-sm btn-success"
                  >
                    Activate
                  </button>
                )}
                {campaign.status === 'active' && (
                  <>
                    <button
                      onClick={() => handleStatusChange('paused')}
                      className="btn btn-sm btn-warning"
                    >
                      Pause
                    </button>
                    <button
                      onClick={() => handleStatusChange('completed')}
                      className="btn btn-sm btn-primary"
                    >
                      Complete
                    </button>
                  </>
                )}
                {campaign.status === 'paused' && (
                  <button
                    onClick={() => handleStatusChange('active')}
                    className="btn btn-sm btn-success"
                  >
                    Resume
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Media Plans section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Media Plans</h3>
          <Link to={`/media-plans?campaign=${id}`} className="btn btn-primary btn-sm">
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Media Plan
          </Link>
        </div>

        {isLoadingMediaPlans ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : mediaPlans.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <DocumentChartBarIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
            <p>No media plans yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Media Plan
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Version
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Dates
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Budget
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Subcampaigns
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mediaPlans.map((mediaPlan: MediaPlan) => (
                  <tr key={mediaPlan.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        to={`/media-plans/${mediaPlan.id}`}
                        className="text-sm font-medium text-primary-600 hover:text-primary-800"
                      >
                        {mediaPlan.name}
                      </Link>
                      <p className="text-xs text-gray-500">{mediaPlan.code}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      v{mediaPlan.version}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {formatDate(mediaPlan.start_date)} - {formatDate(mediaPlan.end_date)}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {formatCurrency(mediaPlan.total_budget_micros, mediaPlan.currency)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge ${statusColors[mediaPlan.status]}`}>
                        {mediaPlan.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {mediaPlan.subcampaigns_count || 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
