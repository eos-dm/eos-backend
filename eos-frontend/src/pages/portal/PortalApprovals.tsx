/**
 * EOS Platform - Client Portal Approvals
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { portalApi } from '@/services/api';
import type { MediaPlan, Subcampaign } from '@/types';
import {
  CheckCircleIcon,
  XCircleIcon,
  DocumentChartBarIcon,
  ClockIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  ChevronDownIcon,
  ChevronUpIcon,
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

// Channel colors
const channelColors: Record<string, string> = {
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

// Approval Modal
interface ApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  mediaPlan: MediaPlan | null;
  action: 'approve' | 'reject';
  onConfirm: (comment: string) => void;
  isPending: boolean;
}

function ApprovalModal({ isOpen, onClose, mediaPlan, action, onConfirm, isPending }: ApprovalModalProps) {
  const [comment, setComment] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirm(comment);
    setComment('');
  };

  if (!isOpen || !mediaPlan) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6 text-left">
          <div className="flex items-center mb-4">
            {action === 'approve' ? (
              <CheckCircleIcon className="h-8 w-8 text-green-500 mr-3" />
            ) : (
              <XCircleIcon className="h-8 w-8 text-red-500 mr-3" />
            )}
            <h3 className="text-lg font-semibold text-gray-900">
              {action === 'approve' ? 'Approve Media Plan' : 'Reject Media Plan'}
            </h3>
          </div>

          <p className="text-sm text-gray-600 mb-4">
            You are about to {action} <strong>{mediaPlan.name}</strong>.
            {action === 'reject' && ' Please provide a reason for rejection.'}
          </p>

          <form onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comment {action === 'reject' && <span className="text-red-500">*</span>}
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={3}
                required={action === 'reject'}
                className="input"
                placeholder={action === 'approve' ? 'Optional approval notes...' : 'Reason for rejection...'}
              />
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button type="button" onClick={onClose} className="btn btn-secondary">
                Cancel
              </button>
              <button
                type="submit"
                disabled={isPending || (action === 'reject' && !comment.trim())}
                className={`btn ${action === 'approve' ? 'btn-success' : 'btn-danger'}`}
              >
                {isPending ? 'Processing...' : action === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Media Plan Card with Subcampaigns
function MediaPlanCard({
  mediaPlan,
  onApprove,
  onReject,
}: {
  mediaPlan: MediaPlan;
  onApprove: () => void;
  onReject: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const subcampaigns = mediaPlan.subcampaigns || [];

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="p-6 bg-yellow-50 border-b border-yellow-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <ClockIcon className="h-6 w-6 text-yellow-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{mediaPlan.name}</h3>
              <p className="text-sm text-gray-500">
                {mediaPlan.campaign_name} - Version {mediaPlan.version}
              </p>
            </div>
          </div>
          <span className="badge badge-warning">Pending Approval</span>
        </div>
      </div>

      {/* Summary */}
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-sm">
              <p className="text-gray-500">Total Budget</p>
              <p className="text-gray-900 font-semibold">
                {formatCurrency(mediaPlan.total_budget_micros, mediaPlan.currency)}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-sm">
              <p className="text-gray-500">Start Date</p>
              <p className="text-gray-900">{formatDate(mediaPlan.start_date)}</p>
            </div>
          </div>
          <div className="flex items-center">
            <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-sm">
              <p className="text-gray-500">End Date</p>
              <p className="text-gray-900">{formatDate(mediaPlan.end_date)}</p>
            </div>
          </div>
          <div className="flex items-center">
            <DocumentChartBarIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-sm">
              <p className="text-gray-500">Subcampaigns</p>
              <p className="text-gray-900">{subcampaigns.length}</p>
            </div>
          </div>
        </div>

        {mediaPlan.description && (
          <p className="text-sm text-gray-600 mb-4">{mediaPlan.description}</p>
        )}

        {/* Subcampaigns toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          {expanded ? (
            <>
              <ChevronUpIcon className="h-4 w-4 mr-1" />
              Hide Details
            </>
          ) : (
            <>
              <ChevronDownIcon className="h-4 w-4 mr-1" />
              View Subcampaigns ({subcampaigns.length})
            </>
          )}
        </button>

        {/* Subcampaigns table */}
        {expanded && subcampaigns.length > 0 && (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Name
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Channel
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Platform
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Budget
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Impressions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {subcampaigns.map((subcampaign: Subcampaign) => (
                  <tr key={subcampaign.id}>
                    <td className="px-3 py-2 text-sm text-gray-900">{subcampaign.name}</td>
                    <td className="px-3 py-2">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize ${
                          channelColors[subcampaign.channel] || channelColors.other
                        }`}
                      >
                        {subcampaign.channel}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-500">
                      {subcampaign.platform || '-'}
                    </td>
                    <td className="px-3 py-2 text-sm text-right font-medium text-gray-900">
                      {formatCurrency(subcampaign.budget_micros, mediaPlan.currency)}
                    </td>
                    <td className="px-3 py-2 text-sm text-right text-gray-500">
                      {subcampaign.impressions?.toLocaleString() || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end space-x-3">
        <button onClick={onReject} className="btn btn-danger">
          <XCircleIcon className="h-5 w-5 mr-2" />
          Reject
        </button>
        <button onClick={onApprove} className="btn btn-success">
          <CheckCircleIcon className="h-5 w-5 mr-2" />
          Approve
        </button>
      </div>
    </div>
  );
}

export default function PortalApprovals() {
  const queryClient = useQueryClient();
  const [selectedMediaPlan, setSelectedMediaPlan] = useState<MediaPlan | null>(null);
  const [modalAction, setModalAction] = useState<'approve' | 'reject'>('approve');
  const [showModal, setShowModal] = useState(false);

  // Fetch media plans
  const { data: mediaPlansData, isLoading } = useQuery({
    queryKey: ['portal-media-plans'],
    queryFn: portalApi.getMediaPlans,
  });

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: ({ id, comment }: { id: number; comment: string }) =>
      portalApi.approveMediaPlan(id, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal-media-plans'] });
      queryClient.invalidateQueries({ queryKey: ['portal-dashboard'] });
      setShowModal(false);
      setSelectedMediaPlan(null);
    },
  });

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: ({ id, comment }: { id: number; comment: string }) =>
      portalApi.rejectMediaPlan(id, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal-media-plans'] });
      queryClient.invalidateQueries({ queryKey: ['portal-dashboard'] });
      setShowModal(false);
      setSelectedMediaPlan(null);
    },
  });

  const mediaPlans = mediaPlansData?.results || [];
  const pendingMediaPlans = mediaPlans.filter((mp: MediaPlan) => mp.status === 'pending_approval');
  const approvedMediaPlans = mediaPlans.filter((mp: MediaPlan) => mp.status === 'approved');

  const handleApprove = (mediaPlan: MediaPlan) => {
    setSelectedMediaPlan(mediaPlan);
    setModalAction('approve');
    setShowModal(true);
  };

  const handleReject = (mediaPlan: MediaPlan) => {
    setSelectedMediaPlan(mediaPlan);
    setModalAction('reject');
    setShowModal(true);
  };

  const handleConfirm = (comment: string) => {
    if (!selectedMediaPlan) return;

    if (modalAction === 'approve') {
      approveMutation.mutate({ id: selectedMediaPlan.id, comment });
    } else {
      rejectMutation.mutate({ id: selectedMediaPlan.id, comment });
    }
  };

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
        <h1 className="text-2xl font-bold text-gray-900">Approvals</h1>
        <p className="mt-1 text-sm text-gray-500">
          Review and approve media plans for your campaigns
        </p>
      </div>

      {/* Pending Approvals */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ClockIcon className="h-5 w-5 text-yellow-500 mr-2" />
          Pending Approval ({pendingMediaPlans.length})
        </h2>

        {pendingMediaPlans.length === 0 ? (
          <div className="card text-center py-12">
            <CheckCircleIcon className="h-12 w-12 mx-auto text-green-300 mb-2" />
            <p className="text-gray-500">No pending approvals</p>
            <p className="text-sm text-gray-400 mt-1">
              All media plans have been reviewed
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {pendingMediaPlans.map((mediaPlan: MediaPlan) => (
              <MediaPlanCard
                key={mediaPlan.id}
                mediaPlan={mediaPlan}
                onApprove={() => handleApprove(mediaPlan)}
                onReject={() => handleReject(mediaPlan)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Recently Approved */}
      {approvedMediaPlans.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
            Recently Approved ({approvedMediaPlans.length})
          </h2>

          <div className="card overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Media Plan
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Campaign
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Budget
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {approvedMediaPlans.slice(0, 5).map((mediaPlan: MediaPlan) => (
                  <tr key={mediaPlan.id}>
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-900">{mediaPlan.name}</p>
                      <p className="text-xs text-gray-500">v{mediaPlan.version}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {mediaPlan.campaign_name}
                    </td>
                    <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                      {formatCurrency(mediaPlan.total_budget_micros, mediaPlan.currency)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="badge badge-success">Approved</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Approval Modal */}
      <ApprovalModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedMediaPlan(null);
        }}
        mediaPlan={selectedMediaPlan}
        action={modalAction}
        onConfirm={handleConfirm}
        isPending={approveMutation.isPending || rejectMutation.isPending}
      />
    </div>
  );
}
