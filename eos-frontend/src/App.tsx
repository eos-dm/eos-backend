import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

// Layouts
import MainLayout from '@/components/layouts/MainLayout';
import AuthLayout from '@/components/layouts/AuthLayout';
import PortalLayout from '@/components/layouts/PortalLayout';

// Auth Pages
import LoginPage from '@/pages/auth/LoginPage';

// Main Pages
import DashboardPage from '@/pages/DashboardPage';
import ProjectsPage from '@/pages/projects/ProjectsPage';
import ProjectDetailPage from '@/pages/projects/ProjectDetailPage';
import CampaignsPage from '@/pages/campaigns/CampaignsPage';
import CampaignDetailPage from '@/pages/campaigns/CampaignDetailPage';
import MediaPlansPage from '@/pages/mediaplans/MediaPlansPage';
import MediaPlanDetailPage from '@/pages/mediaplans/MediaPlanDetailPage';
import ReportsPage from '@/pages/reports/ReportsPage';

// Admin Pages
import UsersPage from '@/pages/admin/UsersPage';
import ClientsPage from '@/pages/admin/ClientsPage';
import LabelsPage from '@/pages/admin/LabelsPage';
import WorkflowsPage from '@/pages/admin/WorkflowsPage';

// Portal Pages
import PortalDashboard from '@/pages/portal/PortalDashboard';
import PortalCampaigns from '@/pages/portal/PortalCampaigns';
import PortalApprovals from '@/pages/portal/PortalApprovals';

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Portal Route Component
const PortalRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, user, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user?.is_client_portal_user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Main App Routes */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />

        {/* Module 4: Projects & Campaigns */}
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:id" element={<ProjectDetailPage />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
        <Route path="/campaigns/:id" element={<CampaignDetailPage />} />
        <Route path="/media-plans" element={<MediaPlansPage />} />
        <Route path="/media-plans/:id" element={<MediaPlanDetailPage />} />

        {/* Module 6: Reports */}
        <Route path="/reports" element={<ReportsPage />} />

        {/* Admin Routes */}
        <Route path="/admin/users" element={<UsersPage />} />
        <Route path="/admin/clients" element={<ClientsPage />} />
        <Route path="/admin/labels" element={<LabelsPage />} />
        <Route path="/admin/workflows" element={<WorkflowsPage />} />
      </Route>

      {/* Client Portal Routes */}
      <Route
        element={
          <PortalRoute>
            <PortalLayout />
          </PortalRoute>
        }
      >
        <Route path="/portal" element={<Navigate to="/portal/dashboard" replace />} />
        <Route path="/portal/dashboard" element={<PortalDashboard />} />
        <Route path="/portal/campaigns" element={<PortalCampaigns />} />
        <Route path="/portal/approvals" element={<PortalApprovals />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
