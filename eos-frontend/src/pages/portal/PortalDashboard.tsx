/**
 * EOS Platform - Client Portal Dashboard
 */
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { portalApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import {
  MegaphoneIcon,
  ClipboardDocumentCheckIcon,
  DocumentChartBarIcon,
  CurrencyDollarIcon,
  ClockIcon,
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

// KPI Card
function KPICard({
  title,
  value,
  icon: Icon,
  color = 'blue',
  link,
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color?: string;
  link?: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  const content = (
    <div className="card p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center">
        <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4">
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{title}</p>
        </div>
      </div>
    </div>
  );

  if (link) {
    return <Link to={link}>{content}</Link>;
  }

  return content;
}

export default function PortalDashboard() {
  const { user } = useAuthStore();

  // Fetch portal dashboard data
  const { isLoading } = useQuery({
    queryKey: ['portal-dashboard'],
    queryFn: portalApi.getDashboard,
  });

  // Fetch campaigns
  const { data: campaignsData } = useQuery({
    queryKey: ['portal-campaigns'],
    queryFn: portalApi.getCampaigns,
  });

  // Fetch media plans for approval
  const { data: mediaPlansData } = useQuery({
    queryKey: ['portal-media-plans'],
    queryFn: portalApi.getMediaPlans,
  });

  const campaigns = campaignsData?.results || [];
  const mediaPlans = mediaPlansData?.results || [];
  const pendingApprovals = mediaPlans.filter((mp: any) => mp.status === 'pending_approval');
  const activeCampaigns = campaigns.filter((c: any) => c.status === 'active');
  const totalBudget = campaigns.reduce((sum: number, c: any) => sum + c.budget_micros, 0);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome message */}
      <div className="card p-6 bg-gradient-to-r from-primary-500 to-primary-600 text-white">
        <h1 className="text-2xl font-bold">Welcome, {user?.first_name}!</h1>
        <p className="mt-1 text-primary-100">
          Here's an overview of your campaigns and pending approvals.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Active Campaigns"
          value={activeCampaigns.length}
          icon={MegaphoneIcon}
          color="blue"
          link="/portal/campaigns"
        />
        <KPICard
          title="Pending Approvals"
          value={pendingApprovals.length}
          icon={ClipboardDocumentCheckIcon}
          color={pendingApprovals.length > 0 ? 'yellow' : 'green'}
          link="/portal/approvals"
        />
        <KPICard
          title="Total Budget"
          value={formatCurrency(totalBudget)}
          icon={CurrencyDollarIcon}
          color="green"
        />
        <KPICard
          title="Media Plans"
          value={mediaPlans.length}
          icon={DocumentChartBarIcon}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Campaigns */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Campaigns</h3>
            <Link
              to="/portal/campaigns"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </div>

          {campaigns.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <MegaphoneIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
              <p>No campaigns yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {campaigns.slice(0, 5).map((campaign: any) => (
                <div
                  key={campaign.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{campaign.name}</p>
                    <p className="text-sm text-gray-500">
                      {formatDate(campaign.start_date)} - {formatDate(campaign.end_date)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {formatCurrency(campaign.budget_micros, campaign.currency)}
                    </p>
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
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Approvals */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Pending Approvals</h3>
            <Link
              to="/portal/approvals"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </div>

          {pendingApprovals.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ClipboardDocumentCheckIcon className="h-12 w-12 mx-auto text-green-300 mb-2" />
              <p>No pending approvals</p>
              <p className="text-sm mt-1">All media plans have been reviewed</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingApprovals.slice(0, 5).map((mediaPlan: any) => (
                <Link
                  key={mediaPlan.id}
                  to="/portal/approvals"
                  className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors"
                >
                  <div>
                    <p className="font-medium text-gray-900">{mediaPlan.name}</p>
                    <p className="text-sm text-gray-500">{mediaPlan.campaign_name}</p>
                  </div>
                  <div className="flex items-center text-yellow-600">
                    <ClockIcon className="h-5 w-5 mr-1" />
                    <span className="text-sm font-medium">Pending</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Link
            to="/portal/campaigns"
            className="flex items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <MegaphoneIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="font-medium text-gray-900">View Campaigns</p>
              <p className="text-sm text-gray-500">See all your campaigns</p>
            </div>
          </Link>
          <Link
            to="/portal/approvals"
            className="flex items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <ClipboardDocumentCheckIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="font-medium text-gray-900">Review Approvals</p>
              <p className="text-sm text-gray-500">
                {pendingApprovals.length} pending
              </p>
            </div>
          </Link>
          <div className="flex items-center p-4 bg-gray-50 rounded-xl">
            <DocumentChartBarIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="font-medium text-gray-900">Media Plans</p>
              <p className="text-sm text-gray-500">{mediaPlans.length} total</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
