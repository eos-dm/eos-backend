/**
 * EOS Platform - TypeScript Type Definitions
 */

// User and Authentication Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone?: string;
  profile_image?: string;
  language: 'es' | 'en';
  timezone: string;
  is_active: boolean;
  is_client_portal_user: boolean;
  last_login?: string;
  created_at: string;
}

export type UserRole =
  | 'superadmin'
  | 'tenant_admin'
  | 'planner'
  | 'finance'
  | 'client_manager'
  | 'viewer';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

// Multi-tenant Types
export interface Tenant {
  id: number;
  name: string;
  slug: string;
  default_currency: string;
  logo?: string;
  primary_color?: string;
  settings: Record<string, any>;
  is_active: boolean;
}

export interface Agency {
  id: number;
  tenant: number;
  name: string;
  code: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  is_active: boolean;
}

export interface CostCenter {
  id: number;
  agency: number;
  agency_name?: string;
  name: string;
  code: string;
  is_active: boolean;
}

export interface Client {
  id: number;
  cost_center: number;
  cost_center_name?: string;
  agency_name?: string;
  name: string;
  code: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  logo?: string;
  is_active: boolean;
}

export interface Advertiser {
  id: number;
  client: number;
  client_name?: string;
  name: string;
  code: string;
  industry?: string;
  website?: string;
  is_active: boolean;
}

// Campaign Module Types
export interface Project {
  id: number;
  advertiser: number;
  advertiser_name?: string;
  client_name?: string;
  name: string;
  code: string;
  description?: string;
  start_date: string;
  end_date?: string;
  status: ProjectStatus;
  total_budget_micros: number;
  currency: string;
  owner: number;
  owner_name?: string;
  campaigns_count?: number;
  created_at: string;
  updated_at: string;
}

export type ProjectStatus = 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';

export interface Campaign {
  id: number;
  project: number;
  project_name?: string;
  name: string;
  code: string;
  description?: string;
  campaign_type: CampaignType;
  objective?: string;
  start_date: string;
  end_date: string;
  status: CampaignStatus;
  budget_micros: number;
  spent_micros: number;
  currency: string;
  target_audience?: string;
  media_plans_count?: number;
  created_at: string;
  updated_at: string;
}

export type CampaignType = 'brand' | 'performance' | 'awareness' | 'consideration' | 'conversion';
export type CampaignStatus = 'draft' | 'pending_approval' | 'approved' | 'active' | 'paused' | 'completed' | 'cancelled';

export interface MediaPlan {
  id: number;
  campaign: number;
  campaign_name?: string;
  name: string;
  code: string;
  description?: string;
  version: number;
  status: MediaPlanStatus;
  start_date: string;
  end_date: string;
  total_budget_micros: number;
  currency: string;
  subcampaigns?: Subcampaign[];
  subcampaigns_count?: number;
  created_at: string;
  updated_at: string;
}

export type MediaPlanStatus = 'draft' | 'pending_approval' | 'approved' | 'active' | 'completed';

export interface Subcampaign {
  id: number;
  media_plan: number;
  name: string;
  channel: ChannelType;
  platform?: string;
  ad_format?: string;
  buy_type: BuyType;
  start_date: string;
  end_date: string;
  budget_micros: number;
  impressions?: number;
  clicks?: number;
  cpm_micros?: number;
  cpc_micros?: number;
  kpi_target?: string;
  notes?: string;
  versions?: SubcampaignVersion[];
  fees?: SubcampaignFee[];
}

export type ChannelType =
  | 'programmatic'
  | 'social'
  | 'search'
  | 'display'
  | 'video'
  | 'native'
  | 'audio'
  | 'ooh'
  | 'tv'
  | 'print'
  | 'other';

export type BuyType = 'cpm' | 'cpc' | 'cpa' | 'cpv' | 'cpl' | 'flat_fee';

export interface SubcampaignVersion {
  id: number;
  subcampaign: number;
  version_number: number;
  name: string;
  budget_micros: number;
  is_current: boolean;
  created_by: number;
  created_at: string;
}

export interface SubcampaignFee {
  id: number;
  subcampaign: number;
  fee_type: FeeType;
  description: string;
  percentage?: number;
  fixed_amount_micros?: number;
  calculated_amount_micros: number;
}

export type FeeType = 'agency_fee' | 'tech_fee' | 'data_fee' | 'verification' | 'other';

// Labels Types
export interface LabelDefinition {
  id: number;
  name: string;
  code: string;
  description?: string;
  label_type: LabelType;
  is_hierarchical: boolean;
  max_levels: number;
  is_required: boolean;
  is_active: boolean;
  display_order: number;
  levels?: LabelLevel[];
  values_count?: number;
}

export type LabelType = 'single' | 'multiple' | 'hierarchical';

export interface LabelLevel {
  id: number;
  label_definition: number;
  level: number;
  name: string;
  code: string;
}

export interface LabelValue {
  id: number;
  label_definition: number;
  label_level?: number;
  parent?: number;
  name: string;
  code: string;
  full_path?: string;
  is_active: boolean;
  children?: LabelValue[];
}

// Workflow Types
export interface WorkflowDefinition {
  id: number;
  name: string;
  code: string;
  description?: string;
  entity_type: EntityType;
  is_active: boolean;
  is_default: boolean;
  states?: WorkflowState[];
  transitions?: WorkflowTransition[];
}

export type EntityType = 'campaign' | 'media_plan' | 'subcampaign' | 'project';

export interface WorkflowState {
  id: number;
  workflow: number;
  name: string;
  code: string;
  state_type: StateType;
  color?: string;
  description?: string;
  is_editable: boolean;
  requires_approval: boolean;
  display_order: number;
}

export type StateType = 'initial' | 'intermediate' | 'final';

export interface WorkflowTransition {
  id: number;
  workflow: number;
  name: string;
  code: string;
  from_state: number;
  to_state: number;
  requires_approval: boolean;
  allowed_groups?: number[];
}

export interface WorkflowInstance {
  id: number;
  workflow: number;
  workflow_name?: string;
  current_state: number;
  current_state_name?: string;
  is_active: boolean;
  started_at: string;
  completed_at?: string;
  available_transitions?: WorkflowTransition[];
}

export interface ApprovalRequest {
  id: number;
  workflow_instance: number;
  transition: number;
  status: ApprovalStatus;
  requested_by: number;
  requested_at: string;
  due_date?: string;
  message?: string;
  responses?: ApprovalResponse[];
}

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';

export interface ApprovalResponse {
  id: number;
  approval_request: number;
  user: number;
  user_name?: string;
  is_approved: boolean;
  comment?: string;
  responded_at: string;
}

// Reports Types
export interface Dashboard {
  id: number;
  name: string;
  description?: string;
  dashboard_type: DashboardType;
  is_default: boolean;
  layout: Record<string, any>;
  widgets?: DashboardWidget[];
}

export type DashboardType = 'overview' | 'campaigns' | 'finance' | 'performance' | 'custom';

export interface DashboardWidget {
  id: number;
  dashboard: number;
  widget_type: WidgetType;
  title: string;
  config: Record<string, any>;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
}

export type WidgetType = 'kpi_card' | 'chart_line' | 'chart_bar' | 'chart_pie' | 'table' | 'map' | 'calendar';

export interface SavedReport {
  id: number;
  name: string;
  description?: string;
  report_type: string;
  filters: Record<string, any>;
  columns: string[];
  is_scheduled: boolean;
  schedule_frequency?: string;
}

// Dashboard KPI Types
export interface DashboardKPI {
  active_campaigns: number;
  total_budget: number;
  total_spent: number;
  budget_utilization: number;
  pending_approvals: number;
  active_projects: number;
  campaigns_by_status: Record<string, number>;
  budget_by_channel: Record<string, number>;
  recent_activities: Activity[];
}

export interface Activity {
  id: number;
  type: string;
  description: string;
  user_name: string;
  timestamp: string;
  entity_type?: string;
  entity_id?: number;
  entity_name?: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// Form Types
export interface ProjectFormData {
  advertiser: number;
  name: string;
  code: string;
  description?: string;
  start_date: string;
  end_date?: string;
  total_budget_micros: number;
  currency: string;
}

export interface CampaignFormData {
  project: number;
  name: string;
  code: string;
  description?: string;
  campaign_type: CampaignType;
  objective?: string;
  start_date: string;
  end_date: string;
  budget_micros: number;
  currency: string;
  target_audience?: string;
}

export interface MediaPlanFormData {
  campaign: number;
  name: string;
  code: string;
  description?: string;
  start_date: string;
  end_date: string;
  total_budget_micros: number;
  currency: string;
}

export interface SubcampaignFormData {
  media_plan: number;
  name: string;
  channel: ChannelType;
  platform?: string;
  ad_format?: string;
  buy_type: BuyType;
  start_date: string;
  end_date: string;
  budget_micros: number;
  impressions?: number;
  clicks?: number;
  cpm_micros?: number;
  cpc_micros?: number;
  kpi_target?: string;
  notes?: string;
}

// Filter Types
export interface ProjectFilters {
  search?: string;
  status?: ProjectStatus;
  advertiser?: number;
  client?: number;
  start_date_after?: string;
  start_date_before?: string;
}

export interface CampaignFilters {
  search?: string;
  status?: CampaignStatus;
  project?: number;
  campaign_type?: CampaignType;
  start_date_after?: string;
  end_date_before?: string;
}

export interface MediaPlanFilters {
  search?: string;
  status?: MediaPlanStatus;
  campaign?: number;
}

// Utility Types
export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  field: string;
  direction: SortDirection;
}

export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}
