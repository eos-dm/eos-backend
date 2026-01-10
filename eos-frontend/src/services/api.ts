/**
 * EOS Platform - API Service Layer
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  User,
  LoginCredentials,
  LoginResponse,
  Project,
  Campaign,
  MediaPlan,
  Subcampaign,
  LabelDefinition,
  LabelValue,
  WorkflowDefinition,
  WorkflowInstance,
  ApprovalRequest,
  Dashboard,
  DashboardKPI,
  PaginatedResponse,
  ProjectFormData,
  CampaignFormData,
  MediaPlanFormData,
  SubcampaignFormData,
  ProjectFilters,
  CampaignFilters,
  MediaPlanFilters,
  Tenant,
  Agency,
  CostCenter,
  Client,
  Advertiser,
} from '@/types';

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStorage = localStorage.getItem('eos-auth-storage');
    if (authStorage) {
      const { state } = JSON.parse(authStorage);
      if (state?.tokens?.access) {
        config.headers.Authorization = `Bearer ${state.tokens.access}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const authStorage = localStorage.getItem('eos-auth-storage');
        if (authStorage) {
          const { state } = JSON.parse(authStorage);
          if (state?.tokens?.refresh) {
            const response = await axios.post(`${API_BASE_URL}/accounts/token/refresh/`, {
              refresh: state.tokens.refresh,
            });

            const newTokens = response.data;
            const newState = {
              ...state,
              tokens: { ...state.tokens, access: newTokens.access },
            };
            localStorage.setItem('eos-auth-storage', JSON.stringify({ state: newState }));

            originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        localStorage.removeItem('eos-auth-storage');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ================== Authentication API ==================
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login/', credentials);
    return response.data;
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout/', { refresh: refreshToken });
  },

  refreshToken: async (refreshToken: string): Promise<{ access: string }> => {
    const response = await apiClient.post('/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/users/me/');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch('/auth/users/me/', data);
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/auth/users/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};

// ================== Core/Hierarchy API ==================
export const coreApi = {
  // Tenants
  getTenants: async (): Promise<PaginatedResponse<Tenant>> => {
    const response = await apiClient.get('/tenants/');
    return response.data;
  },

  getCurrentTenant: async (): Promise<Tenant> => {
    const response = await apiClient.get('/tenants/current/');
    return response.data;
  },

  // Agencies
  getAgencies: async (params?: Record<string, any>): Promise<PaginatedResponse<Agency>> => {
    const response = await apiClient.get('/agencies/', { params });
    return response.data;
  },

  getAgency: async (id: number): Promise<Agency> => {
    const response = await apiClient.get(`/agencies/${id}/`);
    return response.data;
  },

  // Cost Centers
  getCostCenters: async (params?: Record<string, any>): Promise<PaginatedResponse<CostCenter>> => {
    const response = await apiClient.get('/cost-centers/', { params });
    return response.data;
  },

  getCostCenter: async (id: number): Promise<CostCenter> => {
    const response = await apiClient.get(`/cost-centers/${id}/`);
    return response.data;
  },

  // Clients
  getClients: async (params?: Record<string, any>): Promise<PaginatedResponse<Client>> => {
    const response = await apiClient.get('/clients/', { params });
    return response.data;
  },

  getClient: async (id: number): Promise<Client> => {
    const response = await apiClient.get(`/clients/${id}/`);
    return response.data;
  },

  createClient: async (data: Partial<Client>): Promise<Client> => {
    const response = await apiClient.post('/clients/', data);
    return response.data;
  },

  updateClient: async (id: number, data: Partial<Client>): Promise<Client> => {
    const response = await apiClient.patch(`/clients/${id}/`, data);
    return response.data;
  },

  // Advertisers
  getAdvertisers: async (params?: Record<string, any>): Promise<PaginatedResponse<Advertiser>> => {
    const response = await apiClient.get('/advertisers/', { params });
    return response.data;
  },

  getAdvertiser: async (id: number): Promise<Advertiser> => {
    const response = await apiClient.get(`/advertisers/${id}/`);
    return response.data;
  },

  createAdvertiser: async (data: Partial<Advertiser>): Promise<Advertiser> => {
    const response = await apiClient.post('/advertisers/', data);
    return response.data;
  },

  updateAdvertiser: async (id: number, data: Partial<Advertiser>): Promise<Advertiser> => {
    const response = await apiClient.patch(`/advertisers/${id}/`, data);
    return response.data;
  },
};

// ================== Users API ==================
export const usersApi = {
  getUsers: async (params?: Record<string, any>): Promise<PaginatedResponse<User>> => {
    const response = await apiClient.get('/accounts/users/', { params });
    return response.data;
  },

  getUser: async (id: number): Promise<User> => {
    const response = await apiClient.get(`/accounts/users/${id}/`);
    return response.data;
  },

  createUser: async (data: Partial<User> & { password: string }): Promise<User> => {
    const response = await apiClient.post('/accounts/users/', data);
    return response.data;
  },

  updateUser: async (id: number, data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch(`/accounts/users/${id}/`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await apiClient.delete(`/accounts/users/${id}/`);
  },
};

// ================== Projects API ==================
export const projectsApi = {
  getProjects: async (filters?: ProjectFilters): Promise<PaginatedResponse<Project>> => {
    const response = await apiClient.get('/campaigns/projects/', { params: filters });
    return response.data;
  },

  getProject: async (id: number): Promise<Project> => {
    const response = await apiClient.get(`/campaigns/projects/${id}/`);
    return response.data;
  },

  createProject: async (data: ProjectFormData): Promise<Project> => {
    const response = await apiClient.post('/campaigns/projects/', data);
    return response.data;
  },

  updateProject: async (id: number, data: Partial<ProjectFormData>): Promise<Project> => {
    const response = await apiClient.patch(`/campaigns/projects/${id}/`, data);
    return response.data;
  },

  deleteProject: async (id: number): Promise<void> => {
    await apiClient.delete(`/campaigns/projects/${id}/`);
  },

  duplicateProject: async (id: number): Promise<Project> => {
    const response = await apiClient.post(`/campaigns/projects/${id}/duplicate/`);
    return response.data;
  },

  changeProjectStatus: async (id: number, status: string): Promise<Project> => {
    const response = await apiClient.post(`/campaigns/projects/${id}/change_status/`, { status });
    return response.data;
  },
};

// ================== Campaigns API ==================
export const campaignsApi = {
  getCampaigns: async (filters?: CampaignFilters): Promise<PaginatedResponse<Campaign>> => {
    const response = await apiClient.get('/campaigns/campaigns/', { params: filters });
    return response.data;
  },

  getCampaign: async (id: number): Promise<Campaign> => {
    const response = await apiClient.get(`/campaigns/campaigns/${id}/`);
    return response.data;
  },

  createCampaign: async (data: CampaignFormData): Promise<Campaign> => {
    const response = await apiClient.post('/campaigns/campaigns/', data);
    return response.data;
  },

  updateCampaign: async (id: number, data: Partial<CampaignFormData>): Promise<Campaign> => {
    const response = await apiClient.patch(`/campaigns/campaigns/${id}/`, data);
    return response.data;
  },

  deleteCampaign: async (id: number): Promise<void> => {
    await apiClient.delete(`/campaigns/campaigns/${id}/`);
  },

  duplicateCampaign: async (id: number): Promise<Campaign> => {
    const response = await apiClient.post(`/campaigns/campaigns/${id}/duplicate/`);
    return response.data;
  },

  changeCampaignStatus: async (id: number, status: string): Promise<Campaign> => {
    const response = await apiClient.post(`/campaigns/campaigns/${id}/change_status/`, { status });
    return response.data;
  },
};

// ================== Media Plans API ==================
export const mediaPlansApi = {
  getMediaPlans: async (filters?: MediaPlanFilters): Promise<PaginatedResponse<MediaPlan>> => {
    const response = await apiClient.get('/campaigns/media-plans/', { params: filters });
    return response.data;
  },

  getMediaPlan: async (id: number): Promise<MediaPlan> => {
    const response = await apiClient.get(`/campaigns/media-plans/${id}/`);
    return response.data;
  },

  createMediaPlan: async (data: MediaPlanFormData): Promise<MediaPlan> => {
    const response = await apiClient.post('/campaigns/media-plans/', data);
    return response.data;
  },

  updateMediaPlan: async (id: number, data: Partial<MediaPlanFormData>): Promise<MediaPlan> => {
    const response = await apiClient.patch(`/campaigns/media-plans/${id}/`, data);
    return response.data;
  },

  deleteMediaPlan: async (id: number): Promise<void> => {
    await apiClient.delete(`/campaigns/media-plans/${id}/`);
  },

  duplicateMediaPlan: async (id: number): Promise<MediaPlan> => {
    const response = await apiClient.post(`/campaigns/media-plans/${id}/duplicate/`);
    return response.data;
  },

  createVersion: async (id: number): Promise<MediaPlan> => {
    const response = await apiClient.post(`/campaigns/media-plans/${id}/create_version/`);
    return response.data;
  },

  approveMediaPlan: async (id: number, comment?: string): Promise<MediaPlan> => {
    const response = await apiClient.post(`/campaigns/media-plans/${id}/approve/`, { comment });
    return response.data;
  },
};

// ================== Subcampaigns API ==================
export const subcampaignsApi = {
  getSubcampaigns: async (mediaPlanId?: number): Promise<PaginatedResponse<Subcampaign>> => {
    const params = mediaPlanId ? { media_plan: mediaPlanId } : {};
    const response = await apiClient.get('/campaigns/subcampaigns/', { params });
    return response.data;
  },

  getSubcampaign: async (id: number): Promise<Subcampaign> => {
    const response = await apiClient.get(`/campaigns/subcampaigns/${id}/`);
    return response.data;
  },

  createSubcampaign: async (data: SubcampaignFormData): Promise<Subcampaign> => {
    const response = await apiClient.post('/campaigns/subcampaigns/', data);
    return response.data;
  },

  updateSubcampaign: async (id: number, data: Partial<SubcampaignFormData>): Promise<Subcampaign> => {
    const response = await apiClient.patch(`/campaigns/subcampaigns/${id}/`, data);
    return response.data;
  },

  deleteSubcampaign: async (id: number): Promise<void> => {
    await apiClient.delete(`/campaigns/subcampaigns/${id}/`);
  },

  createVersion: async (id: number): Promise<Subcampaign> => {
    const response = await apiClient.post(`/campaigns/subcampaigns/${id}/create_version/`);
    return response.data;
  },
};

// ================== Labels API ==================
export const labelsApi = {
  getLabelDefinitions: async (): Promise<PaginatedResponse<LabelDefinition>> => {
    const response = await apiClient.get('/labels/definitions/');
    return response.data;
  },

  getLabelDefinition: async (id: number): Promise<LabelDefinition> => {
    const response = await apiClient.get(`/labels/definitions/${id}/`);
    return response.data;
  },

  createLabelDefinition: async (data: Partial<LabelDefinition>): Promise<LabelDefinition> => {
    const response = await apiClient.post('/labels/definitions/', data);
    return response.data;
  },

  updateLabelDefinition: async (id: number, data: Partial<LabelDefinition>): Promise<LabelDefinition> => {
    const response = await apiClient.patch(`/labels/definitions/${id}/`, data);
    return response.data;
  },

  deleteLabelDefinition: async (id: number): Promise<void> => {
    await apiClient.delete(`/labels/definitions/${id}/`);
  },

  getLabelValues: async (definitionId?: number): Promise<PaginatedResponse<LabelValue>> => {
    const params = definitionId ? { label_definition: definitionId } : {};
    const response = await apiClient.get('/labels/values/', { params });
    return response.data;
  },

  getLabelValueTree: async (definitionId: number): Promise<LabelValue[]> => {
    const response = await apiClient.get(`/labels/definitions/${definitionId}/value_tree/`);
    return response.data;
  },

  createLabelValue: async (data: Partial<LabelValue>): Promise<LabelValue> => {
    const response = await apiClient.post('/labels/values/', data);
    return response.data;
  },

  updateLabelValue: async (id: number, data: Partial<LabelValue>): Promise<LabelValue> => {
    const response = await apiClient.patch(`/labels/values/${id}/`, data);
    return response.data;
  },

  deleteLabelValue: async (id: number): Promise<void> => {
    await apiClient.delete(`/labels/values/${id}/`);
  },
};

// ================== Workflows API ==================
export const workflowsApi = {
  getWorkflowDefinitions: async (): Promise<PaginatedResponse<WorkflowDefinition>> => {
    const response = await apiClient.get('/workflows/definitions/');
    return response.data;
  },

  getWorkflowDefinition: async (id: number): Promise<WorkflowDefinition> => {
    const response = await apiClient.get(`/workflows/definitions/${id}/`);
    return response.data;
  },

  getWorkflowInstance: async (id: number): Promise<WorkflowInstance> => {
    const response = await apiClient.get(`/workflows/instances/${id}/`);
    return response.data;
  },

  executeTransition: async (instanceId: number, transitionId: number, comment?: string): Promise<WorkflowInstance> => {
    const response = await apiClient.post(`/workflows/instances/${instanceId}/execute_transition/`, {
      transition_id: transitionId,
      comment,
    });
    return response.data;
  },

  getApprovalRequests: async (status?: string): Promise<PaginatedResponse<ApprovalRequest>> => {
    const params = status ? { status } : {};
    const response = await apiClient.get('/workflows/approvals/', { params });
    return response.data;
  },

  respondToApproval: async (id: number, isApproved: boolean, comment?: string): Promise<ApprovalRequest> => {
    const response = await apiClient.post(`/workflows/approvals/${id}/respond/`, {
      is_approved: isApproved,
      comment,
    });
    return response.data;
  },
};

// ================== Reports/Dashboard API ==================
export const reportsApi = {
  getDashboardData: async (): Promise<DashboardKPI> => {
    const response = await apiClient.get('/reports/dashboard/');
    return response.data;
  },

  getDashboards: async (): Promise<PaginatedResponse<Dashboard>> => {
    const response = await apiClient.get('/reports/dashboards/');
    return response.data;
  },

  getDashboard: async (id: number): Promise<Dashboard> => {
    const response = await apiClient.get(`/reports/dashboards/${id}/`);
    return response.data;
  },

  getCampaignReport: async (params: Record<string, any>): Promise<any> => {
    const response = await apiClient.get('/reports/campaigns/', { params });
    return response.data;
  },

  getBudgetReport: async (params: Record<string, any>): Promise<any> => {
    const response = await apiClient.get('/reports/budget/', { params });
    return response.data;
  },

  exportReport: async (reportType: string, format: string, filters: Record<string, any>): Promise<Blob> => {
    const response = await apiClient.post(
      '/reports/exports/',
      { report_type: reportType, format, filters },
      { responseType: 'blob' }
    );
    return response.data;
  },
};

// ================== Portal API ==================
export const portalApi = {
  getDashboard: async (): Promise<any> => {
    const response = await apiClient.get('/portal/dashboard/');
    return response.data;
  },

  getCampaigns: async (): Promise<PaginatedResponse<Campaign>> => {
    const response = await apiClient.get('/portal/campaigns/');
    return response.data;
  },

  getCampaign: async (id: number): Promise<Campaign> => {
    const response = await apiClient.get(`/portal/campaigns/${id}/`);
    return response.data;
  },

  getMediaPlans: async (): Promise<PaginatedResponse<MediaPlan>> => {
    const response = await apiClient.get('/portal/media-plans/');
    return response.data;
  },

  approveMediaPlan: async (id: number, comment?: string): Promise<MediaPlan> => {
    const response = await apiClient.post(`/portal/media-plans/${id}/approve/`, { comment });
    return response.data;
  },

  rejectMediaPlan: async (id: number, comment: string): Promise<MediaPlan> => {
    const response = await apiClient.post(`/portal/media-plans/${id}/reject/`, { comment });
    return response.data;
  },
};

export default apiClient;
