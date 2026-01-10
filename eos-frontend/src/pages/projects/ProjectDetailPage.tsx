/**
 * EOS Platform - Project Detail Page
 */
import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, campaignsApi } from '@/services/api';
import type { Project, Campaign } from '@/types';
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  MegaphoneIcon,
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
  active: 'badge-success',
  paused: 'badge-warning',
  completed: 'badge-primary',
  cancelled: 'badge-danger',
  pending_approval: 'badge-warning',
  approved: 'badge-success',
};

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Project>>({});

  // Fetch project
  const { data: project, isLoading: isLoadingProject } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.getProject(parseInt(id!)),
    enabled: !!id,
  });

  // Fetch project campaigns
  const { data: campaignsData, isLoading: isLoadingCampaigns } = useQuery({
    queryKey: ['campaigns', { project: id }],
    queryFn: () => campaignsApi.getCampaigns({ project: parseInt(id!) }),
    enabled: !!id,
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: Partial<Project>) => projectsApi.updateProject(parseInt(id!), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', id] });
      setIsEditing(false);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => projectsApi.deleteProject(parseInt(id!)),
    onSuccess: () => {
      navigate('/projects');
    },
  });

  // Status change mutation
  const statusMutation = useMutation({
    mutationFn: (status: string) => projectsApi.changeProjectStatus(parseInt(id!), status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', id] });
    },
  });

  const handleEdit = () => {
    if (project) {
      setEditForm({
        name: project.name,
        code: project.code,
        description: project.description,
        start_date: project.start_date,
        end_date: project.end_date,
      });
      setIsEditing(true);
    }
  };

  const handleSave = () => {
    updateMutation.mutate(editForm);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      deleteMutation.mutate();
    }
  };

  const handleStatusChange = (newStatus: string) => {
    statusMutation.mutate(newStatus);
  };

  if (isLoadingProject) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Project not found</p>
        <Link to="/projects" className="btn btn-primary mt-4">
          Back to Projects
        </Link>
      </div>
    );
  }

  const campaigns = campaignsData?.results || [];
  const totalCampaignBudget = campaigns.reduce((sum: number, c: Campaign) => sum + c.budget_micros, 0);

  return (
    <div className="space-y-6">
      {/* Back button and header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center">
          <Link
            to="/projects"
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
            <p className="mt-1 text-sm text-gray-500">{project.code}</p>
          </div>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <span className={`badge ${statusColors[project.status]}`}>
            {project.status.replace('_', ' ')}
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

      {/* Project details card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main info */}
        <div className="lg:col-span-2 card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Details</h3>

          {isEditing ? (
            <div className="space-y-4">
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={editForm.description || ''}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={3}
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
              <div>
                <p className="text-sm text-gray-500">Description</p>
                <p className="text-gray-900">{project.description || 'No description'}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Client</p>
                  <p className="text-gray-900">{project.client_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Advertiser</p>
                  <p className="text-gray-900">{project.advertiser_name || '-'}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center">
                  <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm text-gray-500">Start Date</p>
                    <p className="text-gray-900">{formatDate(project.start_date)}</p>
                  </div>
                </div>
                {project.end_date && (
                  <div className="flex items-center">
                    <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-sm text-gray-500">End Date</p>
                      <p className="text-gray-900">{formatDate(project.end_date)}</p>
                    </div>
                  </div>
                )}
              </div>
              <div>
                <p className="text-sm text-gray-500">Owner</p>
                <p className="text-gray-900">{project.owner_name || '-'}</p>
              </div>
            </div>
          )}
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
                {formatCurrency(project.total_budget_micros, project.currency)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <MegaphoneIcon className="h-5 w-5 text-blue-500 mr-2" />
                <span className="text-sm text-gray-500">Allocated to Campaigns</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(totalCampaignBudget, project.currency)}
              </span>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Remaining</span>
                <span
                  className={`text-lg font-semibold ${
                    project.total_budget_micros - totalCampaignBudget >= 0
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {formatCurrency(project.total_budget_micros - totalCampaignBudget, project.currency)}
                </span>
              </div>
            </div>

            {/* Status actions */}
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-2">Change Status</p>
              <div className="flex flex-wrap gap-2">
                {project.status === 'draft' && (
                  <button
                    onClick={() => handleStatusChange('active')}
                    className="btn btn-sm btn-success"
                  >
                    Activate
                  </button>
                )}
                {project.status === 'active' && (
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
                {project.status === 'paused' && (
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

      {/* Campaigns section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Campaigns</h3>
          <Link to={`/campaigns?project=${id}`} className="btn btn-primary btn-sm">
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Campaign
          </Link>
        </div>

        {isLoadingCampaigns ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MegaphoneIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
            <p>No campaigns yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Campaign
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Type
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
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {campaigns.map((campaign: Campaign) => (
                  <tr key={campaign.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        to={`/campaigns/${campaign.id}`}
                        className="text-sm font-medium text-primary-600 hover:text-primary-800"
                      >
                        {campaign.name}
                      </Link>
                      <p className="text-xs text-gray-500">{campaign.code}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 capitalize">
                      {campaign.campaign_type}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {formatDate(campaign.start_date)} - {formatDate(campaign.end_date)}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {formatCurrency(campaign.budget_micros, campaign.currency)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge ${statusColors[campaign.status]}`}>
                        {campaign.status.replace('_', ' ')}
                      </span>
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
