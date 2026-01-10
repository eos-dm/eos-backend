/**
 * EOS Platform - Media Plan Detail Page
 */
import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mediaPlansApi, subcampaignsApi } from '@/services/api';
import type { Subcampaign, ChannelType, BuyType } from '@/types';
import {
  ArrowLeftIcon,
  TrashIcon,
  PlusIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  CheckCircleIcon,
  DocumentDuplicateIcon,
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
  approved: 'badge-success',
  active: 'badge-primary',
  completed: 'badge-info',
};

// Channel colors
const channelColors: Record<ChannelType, string> = {
  programmatic: 'bg-blue-100 text-blue-700',
  social: 'bg-pink-100 text-pink-700',
  search: 'bg-green-100 text-green-700',
  display: 'bg-purple-100 text-purple-700',
  video: 'bg-red-100 text-red-700',
  native: 'bg-yellow-100 text-yellow-700',
  audio: 'bg-indigo-100 text-indigo-700',
  ooh: 'bg-orange-100 text-orange-700',
  tv: 'bg-cyan-100 text-cyan-700',
  print: 'bg-gray-100 text-gray-700',
  other: 'bg-gray-100 text-gray-700',
};

// Add Subcampaign Modal
interface AddSubcampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  mediaPlanId: number;
}

function AddSubcampaignModal({ isOpen, onClose, mediaPlanId }: AddSubcampaignModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: '',
    channel: 'programmatic' as ChannelType,
    platform: '',
    ad_format: '',
    buy_type: 'cpm' as BuyType,
    start_date: '',
    end_date: '',
    budget_micros: '',
    impressions: '',
    clicks: '',
    cpm_micros: '',
    notes: '',
  });

  const createMutation = useMutation({
    mutationFn: subcampaignsApi.createSubcampaign,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plan'] });
      queryClient.invalidateQueries({ queryKey: ['subcampaigns'] });
      onClose();
      setFormData({
        name: '',
        channel: 'programmatic',
        platform: '',
        ad_format: '',
        buy_type: 'cpm',
        start_date: '',
        end_date: '',
        budget_micros: '',
        impressions: '',
        clicks: '',
        cpm_micros: '',
        notes: '',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      media_plan: mediaPlanId,
      name: formData.name,
      channel: formData.channel,
      platform: formData.platform || undefined,
      ad_format: formData.ad_format || undefined,
      buy_type: formData.buy_type,
      start_date: formData.start_date,
      end_date: formData.end_date,
      budget_micros: Math.round(parseFloat(formData.budget_micros) * 1_000_000),
      impressions: formData.impressions ? parseInt(formData.impressions) : undefined,
      clicks: formData.clicks ? parseInt(formData.clicks) : undefined,
      cpm_micros: formData.cpm_micros ? Math.round(parseFloat(formData.cpm_micros) * 1_000_000) : undefined,
      notes: formData.notes || undefined,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6 text-left max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Subcampaign</h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="input"
                placeholder="Programmatic Display"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
                <select
                  value={formData.channel}
                  onChange={(e) => setFormData({ ...formData, channel: e.target.value as ChannelType })}
                  className="input"
                >
                  <option value="programmatic">Programmatic</option>
                  <option value="social">Social</option>
                  <option value="search">Search</option>
                  <option value="display">Display</option>
                  <option value="video">Video</option>
                  <option value="native">Native</option>
                  <option value="audio">Audio</option>
                  <option value="ooh">OOH</option>
                  <option value="tv">TV</option>
                  <option value="print">Print</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Buy Type</label>
                <select
                  value={formData.buy_type}
                  onChange={(e) => setFormData({ ...formData, buy_type: e.target.value as BuyType })}
                  className="input"
                >
                  <option value="cpm">CPM</option>
                  <option value="cpc">CPC</option>
                  <option value="cpa">CPA</option>
                  <option value="cpv">CPV</option>
                  <option value="cpl">CPL</option>
                  <option value="flat_fee">Flat Fee</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
                <input
                  type="text"
                  value={formData.platform}
                  onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                  className="input"
                  placeholder="Google Ads"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ad Format</label>
                <input
                  type="text"
                  value={formData.ad_format}
                  onChange={(e) => setFormData({ ...formData, ad_format: e.target.value })}
                  className="input"
                  placeholder="Banner 300x250"
                />
              </div>
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Budget</label>
              <input
                type="number"
                value={formData.budget_micros}
                onChange={(e) => setFormData({ ...formData, budget_micros: e.target.value })}
                required
                min="0"
                step="0.01"
                className="input"
                placeholder="1000"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Impressions</label>
                <input
                  type="number"
                  value={formData.impressions}
                  onChange={(e) => setFormData({ ...formData, impressions: e.target.value })}
                  className="input"
                  placeholder="100000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Clicks</label>
                <input
                  type="number"
                  value={formData.clicks}
                  onChange={(e) => setFormData({ ...formData, clicks: e.target.value })}
                  className="input"
                  placeholder="500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">CPM</label>
                <input
                  type="number"
                  value={formData.cpm_micros}
                  onChange={(e) => setFormData({ ...formData, cpm_micros: e.target.value })}
                  step="0.01"
                  className="input"
                  placeholder="5.00"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="input"
                placeholder="Additional notes..."
              />
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
                {createMutation.isPending ? 'Adding...' : 'Add Subcampaign'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function MediaPlanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showAddSubcampaign, setShowAddSubcampaign] = useState(false);

  // Fetch media plan
  const { data: mediaPlan, isLoading: isLoadingMediaPlan } = useQuery({
    queryKey: ['media-plan', id],
    queryFn: () => mediaPlansApi.getMediaPlan(parseInt(id!)),
    enabled: !!id,
  });

  // Fetch subcampaigns
  const { data: subcampaignsData, isLoading: isLoadingSubcampaigns } = useQuery({
    queryKey: ['subcampaigns', { media_plan: id }],
    queryFn: () => subcampaignsApi.getSubcampaigns(parseInt(id!)),
    enabled: !!id,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => mediaPlansApi.deleteMediaPlan(parseInt(id!)),
    onSuccess: () => {
      navigate('/media-plans');
    },
  });

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: () => mediaPlansApi.approveMediaPlan(parseInt(id!)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plan', id] });
    },
  });

  // Create version mutation
  const createVersionMutation = useMutation({
    mutationFn: () => mediaPlansApi.createVersion(parseInt(id!)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media-plan', id] });
    },
  });

  // Delete subcampaign mutation
  const deleteSubcampaignMutation = useMutation({
    mutationFn: subcampaignsApi.deleteSubcampaign,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subcampaigns', { media_plan: id }] });
      queryClient.invalidateQueries({ queryKey: ['media-plan', id] });
    },
  });

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this media plan?')) {
      deleteMutation.mutate();
    }
  };

  const handleDeleteSubcampaign = (subcampaignId: number) => {
    if (window.confirm('Are you sure you want to delete this subcampaign?')) {
      deleteSubcampaignMutation.mutate(subcampaignId);
    }
  };

  if (isLoadingMediaPlan) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!mediaPlan) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Media plan not found</p>
        <Link to="/media-plans" className="btn btn-primary mt-4">
          Back to Media Plans
        </Link>
      </div>
    );
  }

  const subcampaigns = subcampaignsData?.results || [];
  const totalSubcampaignBudget = subcampaigns.reduce((sum: number, sc: Subcampaign) => sum + sc.budget_micros, 0);

  return (
    <div className="space-y-6">
      {/* Back button and header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center">
          <Link
            to="/media-plans"
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{mediaPlan.name}</h1>
            <p className="mt-1 text-sm text-gray-500">{mediaPlan.code} - Version {mediaPlan.version}</p>
          </div>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <span className={`badge ${statusColors[mediaPlan.status]}`}>
            {mediaPlan.status.replace('_', ' ')}
          </span>
          {mediaPlan.status === 'pending_approval' && (
            <button onClick={() => approveMutation.mutate()} className="btn btn-success">
              <CheckCircleIcon className="h-4 w-4 mr-2" />
              Approve
            </button>
          )}
          <button onClick={() => createVersionMutation.mutate()} className="btn btn-secondary">
            <DocumentDuplicateIcon className="h-4 w-4 mr-2" />
            New Version
          </button>
          <button onClick={handleDelete} className="btn btn-danger">
            <TrashIcon className="h-4 w-4 mr-2" />
            Delete
          </button>
        </div>
      </div>

      {/* Media Plan details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main info */}
        <div className="lg:col-span-2 card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Media Plan Details</h3>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Campaign</p>
              <Link
                to={`/campaigns/${mediaPlan.campaign}`}
                className="text-primary-600 hover:text-primary-800"
              >
                {mediaPlan.campaign_name || '-'}
              </Link>
            </div>
            <div>
              <p className="text-sm text-gray-500">Description</p>
              <p className="text-gray-900">{mediaPlan.description || 'No description'}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center">
                <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Start Date</p>
                  <p className="text-gray-900">{formatDate(mediaPlan.start_date)}</p>
                </div>
              </div>
              <div className="flex items-center">
                <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">End Date</p>
                  <p className="text-gray-900">{formatDate(mediaPlan.end_date)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Budget summary */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Budget Summary</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-green-500 mr-2" />
                <span className="text-sm text-gray-500">Total Budget</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(mediaPlan.total_budget_micros, mediaPlan.currency)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Allocated to Subcampaigns</span>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(totalSubcampaignBudget, mediaPlan.currency)}
              </span>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Remaining</span>
                <span
                  className={`text-lg font-semibold ${
                    mediaPlan.total_budget_micros - totalSubcampaignBudget >= 0
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {formatCurrency(mediaPlan.total_budget_micros - totalSubcampaignBudget, mediaPlan.currency)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subcampaigns section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Subcampaigns</h3>
          <button onClick={() => setShowAddSubcampaign(true)} className="btn btn-primary btn-sm">
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Subcampaign
          </button>
        </div>

        {isLoadingSubcampaigns ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : subcampaigns.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No subcampaigns yet</p>
            <button
              onClick={() => setShowAddSubcampaign(true)}
              className="btn btn-primary btn-sm mt-4"
            >
              Add your first subcampaign
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Channel
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Platform
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Dates
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Budget
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Impressions
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Buy Type
                  </th>
                  <th className="relative px-4 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {subcampaigns.map((subcampaign: Subcampaign) => (
                  <tr key={subcampaign.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium text-gray-900">
                        {subcampaign.name}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                          channelColors[subcampaign.channel]
                        }`}
                      >
                        {subcampaign.channel}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {subcampaign.platform || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {formatDate(subcampaign.start_date)} - {formatDate(subcampaign.end_date)}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {formatCurrency(subcampaign.budget_micros, mediaPlan.currency)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {subcampaign.impressions?.toLocaleString() || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 uppercase">
                      {subcampaign.buy_type}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleDeleteSubcampaign(subcampaign.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Subcampaign Modal */}
      <AddSubcampaignModal
        isOpen={showAddSubcampaign}
        onClose={() => setShowAddSubcampaign(false)}
        mediaPlanId={parseInt(id!)}
      />
    </div>
  );
}
