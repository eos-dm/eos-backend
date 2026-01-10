/**
 * EOS Platform - Reports Page
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { reportsApi, campaignsApi, projectsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import type { Campaign, Project, DashboardKPI } from '@/types';
import {
  ChartBarIcon,
  ArrowDownTrayIcon,
  FunnelIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  MegaphoneIcon,
  ArrowTrendingUpIcon,
  DocumentChartBarIcon,
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

// Format percentage
const formatPercent = (value: number) => {
  return `${value.toFixed(1)}%`;
};

// Simple Bar Chart Component
function BarChart({ data, label }: { data: Record<string, number>; label: string }) {
  const entries = Object.entries(data);
  const maxValue = Math.max(...entries.map(([, v]) => v), 1);

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-700">{label}</h4>
      {entries.length === 0 ? (
        <p className="text-sm text-gray-500">No data available</p>
      ) : (
        entries.map(([key, value]) => (
          <div key={key}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
              <span className="font-medium text-gray-900">{value}</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 rounded-full transition-all duration-300"
                style={{ width: `${(value / maxValue) * 100}%` }}
              />
            </div>
          </div>
        ))
      )}
    </div>
  );
}

// Budget Bar Chart
function BudgetChart({ data, label }: { data: Record<string, number>; label: string }) {
  const entries = Object.entries(data);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-700">{label}</h4>
      {entries.length === 0 ? (
        <p className="text-sm text-gray-500">No data available</p>
      ) : (
        entries.map(([key, value]) => {
          const percentage = total > 0 ? (value / total) * 100 : 0;
          return (
            <div key={key}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                <span className="font-medium text-gray-900">
                  {formatCurrency(value)} ({formatPercent(percentage)})
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

// KPI Card
function KPICard({
  title,
  value,
  icon: Icon,
  color = 'blue',
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color?: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="card p-4">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="ml-3">
          <p className="text-xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{title}</p>
        </div>
      </div>
    </div>
  );
}

export default function ReportsPage() {
  useAuthStore(); // Keep for potential future use
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [reportType, setReportType] = useState<'overview' | 'campaigns' | 'budget'>('overview');

  // Fetch dashboard KPIs
  const { data: kpis, isLoading: isLoadingKpis } = useQuery<DashboardKPI>({
    queryKey: ['dashboard-kpis'],
    queryFn: reportsApi.getDashboardData,
  });

  // Fetch campaigns
  const { data: campaignsData } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.getCampaigns(),
  });

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.getProjects(),
  });

  const campaigns = campaignsData?.results || [];
  const projects = projectsData?.results || [];

  // Calculate additional metrics
  const totalBudget = campaigns.reduce((sum: number, c: Campaign) => sum + c.budget_micros, 0);
  const totalSpent = campaigns.reduce((sum: number, c: Campaign) => sum + c.spent_micros, 0);

  // Group campaigns by type
  const campaignsByType = campaigns.reduce((acc: Record<string, number>, c: Campaign) => {
    acc[c.campaign_type] = (acc[c.campaign_type] || 0) + 1;
    return acc;
  }, {});

  // Projects by status
  const projectsByStatus = projects.reduce((acc: Record<string, number>, p: Project) => {
    acc[p.status] = (acc[p.status] || 0) + 1;
    return acc;
  }, {});

  const handleExport = async (format: 'csv' | 'xlsx' | 'pdf') => {
    try {
      const blob = await reportsApi.exportReport(reportType, format, {
        start_date: dateRange.start,
        end_date: dateRange.end,
        project: selectedProject || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportType}_${dateRange.start}_${dateRange.end}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  if (isLoadingKpis) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="mt-1 text-sm text-gray-500">
            Analytics and insights for your campaigns
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <button
            onClick={() => handleExport('xlsx')}
            className="btn btn-secondary"
          >
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            Export Excel
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="btn btn-primary"
          >
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            Export PDF
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex items-center gap-2">
            <CalendarIcon className="h-5 w-5 text-gray-400" />
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="input w-40"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="input w-40"
            />
          </div>

          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="input w-48"
          >
            <option value="">All Projects</option>
            {projects.map((project: Project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>

          <div className="flex rounded-lg overflow-hidden border border-gray-300">
            <button
              onClick={() => setReportType('overview')}
              className={`px-4 py-2 text-sm font-medium ${
                reportType === 'overview'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setReportType('campaigns')}
              className={`px-4 py-2 text-sm font-medium ${
                reportType === 'campaigns'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Campaigns
            </button>
            <button
              onClick={() => setReportType('budget')}
              className={`px-4 py-2 text-sm font-medium ${
                reportType === 'budget'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Budget
            </button>
          </div>
        </div>
      </div>

      {/* KPI Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          title="Active Campaigns"
          value={kpis?.active_campaigns || campaigns.filter((c: Campaign) => c.status === 'active').length}
          icon={MegaphoneIcon}
          color="blue"
        />
        <KPICard
          title="Total Budget"
          value={formatCurrency(totalBudget)}
          icon={CurrencyDollarIcon}
          color="green"
        />
        <KPICard
          title="Total Spent"
          value={formatCurrency(totalSpent)}
          icon={ChartBarIcon}
          color="purple"
        />
        <KPICard
          title="Budget Utilization"
          value={formatPercent(totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0)}
          icon={ArrowTrendingUpIcon}
          color={totalSpent / totalBudget > 0.8 ? 'yellow' : 'green'}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaigns by Status */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Campaigns by Status</h3>
            <DocumentChartBarIcon className="h-5 w-5 text-gray-400" />
          </div>
          <BarChart data={kpis?.campaigns_by_status || {}} label="" />
        </div>

        {/* Budget by Channel */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Budget by Channel</h3>
            <CurrencyDollarIcon className="h-5 w-5 text-gray-400" />
          </div>
          <BudgetChart data={kpis?.budget_by_channel || {}} label="" />
        </div>

        {/* Campaigns by Type */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Campaigns by Type</h3>
            <MegaphoneIcon className="h-5 w-5 text-gray-400" />
          </div>
          <BarChart data={campaignsByType} label="" />
        </div>

        {/* Projects by Status */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Projects by Status</h3>
            <FunnelIcon className="h-5 w-5 text-gray-400" />
          </div>
          <BarChart data={projectsByStatus} label="" />
        </div>
      </div>

      {/* Detailed Table */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Details</h3>
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
                  Status
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Budget
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Spent
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Utilization
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {campaigns.slice(0, 10).map((campaign: Campaign) => {
                const utilization = campaign.budget_micros > 0
                  ? (campaign.spent_micros / campaign.budget_micros) * 100
                  : 0;
                return (
                  <tr key={campaign.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium text-gray-900">
                        {campaign.name}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 capitalize">
                      {campaign.campaign_type}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`badge ${
                          campaign.status === 'active'
                            ? 'badge-success'
                            : campaign.status === 'completed'
                            ? 'badge-primary'
                            : 'badge-secondary'
                        }`}
                      >
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-right font-medium">
                      {formatCurrency(campaign.budget_micros, campaign.currency)}
                    </td>
                    <td className="px-4 py-3 text-sm text-right">
                      {formatCurrency(campaign.spent_micros, campaign.currency)}
                    </td>
                    <td className="px-4 py-3 text-sm text-right">
                      <span
                        className={
                          utilization > 90
                            ? 'text-red-600 font-medium'
                            : utilization > 70
                            ? 'text-yellow-600'
                            : 'text-green-600'
                        }
                      >
                        {formatPercent(utilization)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
