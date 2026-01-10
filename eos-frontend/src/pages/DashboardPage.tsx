/**
 * EOS Platform - Dashboard Page
 */
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { reportsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import {
  CurrencyDollarIcon,
  MegaphoneIcon,
  FolderIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';
import type { DashboardKPI } from '@/types';

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

// KPI Card Component
interface KPICardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  trend?: number;
  trendLabel?: string;
  color?: 'blue' | 'green' | 'yellow' | 'purple' | 'red';
}

function KPICard({ title, value, icon: Icon, trend, trendLabel, color = 'blue' }: KPICardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        {trend !== undefined && (
          <div
            className={`flex items-center text-sm ${
              trend >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {trend >= 0 ? (
              <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
            ) : (
              <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
            )}
            {formatPercent(Math.abs(trend))}
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500 mt-1">{title}</p>
        {trendLabel && <p className="text-xs text-gray-400 mt-1">{trendLabel}</p>}
      </div>
    </div>
  );
}

// Status Badge
function StatusBadge({ status, count }: { status: string; count: number }) {
  const statusColors: Record<string, string> = {
    draft: 'badge-secondary',
    active: 'badge-success',
    pending_approval: 'badge-warning',
    completed: 'badge-primary',
    paused: 'badge-secondary',
    cancelled: 'badge-danger',
  };

  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</span>
      <span className={`badge ${statusColors[status] || 'badge-secondary'}`}>{count}</span>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: kpis, isLoading } = useQuery<DashboardKPI>({
    queryKey: ['dashboard-kpis'],
    queryFn: reportsApi.getDashboardData,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const defaultKpis: DashboardKPI = {
    active_campaigns: 0,
    total_budget: 0,
    total_spent: 0,
    budget_utilization: 0,
    pending_approvals: 0,
    active_projects: 0,
    campaigns_by_status: {},
    budget_by_channel: {},
    recent_activities: [],
  };

  const data = kpis || defaultKpis;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Welcome back, {user?.first_name}! Here's your overview.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link to="/campaigns" className="btn btn-primary">
            View All Campaigns
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Active Campaigns"
          value={data.active_campaigns}
          icon={MegaphoneIcon}
          color="blue"
        />
        <KPICard
          title="Total Budget"
          value={formatCurrency(data.total_budget)}
          icon={CurrencyDollarIcon}
          color="green"
        />
        <KPICard
          title="Budget Utilization"
          value={formatPercent(data.budget_utilization)}
          icon={ArrowTrendingUpIcon}
          color="purple"
        />
        <KPICard
          title="Pending Approvals"
          value={data.pending_approvals}
          icon={ClockIcon}
          color={data.pending_approvals > 0 ? 'yellow' : 'green'}
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Campaigns by Status */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaigns by Status</h3>
          <div className="divide-y divide-gray-100">
            {Object.entries(data.campaigns_by_status).length > 0 ? (
              Object.entries(data.campaigns_by_status).map(([status, count]) => (
                <StatusBadge key={status} status={status} count={count} />
              ))
            ) : (
              <p className="text-sm text-gray-500 py-4 text-center">No campaigns yet</p>
            )}
          </div>
          <Link
            to="/campaigns"
            className="block mt-4 text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View all campaigns
          </Link>
        </div>

        {/* Budget by Channel */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Budget by Channel</h3>
          <div className="space-y-3">
            {Object.entries(data.budget_by_channel).length > 0 ? (
              Object.entries(data.budget_by_channel).map(([channel, budget]) => {
                const percentage = data.total_budget > 0 ? (budget / data.total_budget) * 100 : 0;
                return (
                  <div key={channel}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 capitalize">{channel}</span>
                      <span className="font-medium text-gray-900">
                        {formatCurrency(budget)}
                      </span>
                    </div>
                    <div className="mt-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-sm text-gray-500 py-4 text-center">No budget data yet</p>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {data.recent_activities.length > 0 ? (
              data.recent_activities.slice(0, 5).map((activity) => (
                <div key={activity.id} className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-600">
                      {activity.user_name?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-gray-900">{activity.description}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleString('es-ES')}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 py-4 text-center">No recent activity</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/projects"
            className="flex flex-col items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <FolderIcon className="h-8 w-8 text-gray-600 mb-2" />
            <span className="text-sm font-medium text-gray-700">New Project</span>
          </Link>
          <Link
            to="/campaigns"
            className="flex flex-col items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <MegaphoneIcon className="h-8 w-8 text-gray-600 mb-2" />
            <span className="text-sm font-medium text-gray-700">New Campaign</span>
          </Link>
          <Link
            to="/media-plans"
            className="flex flex-col items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <CurrencyDollarIcon className="h-8 w-8 text-gray-600 mb-2" />
            <span className="text-sm font-medium text-gray-700">Media Plan</span>
          </Link>
          <Link
            to="/reports"
            className="flex flex-col items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <ArrowTrendingUpIcon className="h-8 w-8 text-gray-600 mb-2" />
            <span className="text-sm font-medium text-gray-700">View Reports</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
