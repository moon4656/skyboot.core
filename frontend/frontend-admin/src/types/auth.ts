// 인증 관련 타입 정의
export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  first_name?: string
  last_name?: string
  avatar?: string
  position?: string
  organization_id?: number
  description?: string
  email_verified?: boolean
  is_active: boolean
  roles?: Role[]
  additional_permissions?: Permission[]
  last_login?: string
  created_at: string
  updated_at: string
}

export interface Permission {
  id: number
  name: string
  code?: string
  description?: string
  display_name?: string
  resource: string
  action: string
  category?: string
  is_active?: boolean
  user_count?: number
  created_at: string
  updated_at: string
}

export interface Role {
  id: number
  name: string
  description?: string
  display_name?: string
  permissions: Permission[]
  created_at: string
  updated_at: string
}

export interface UserRole {
  id: number
  user_id: number
  role_id: number
  user: User
  role: Role
  created_at: string
  updated_at: string
}

export interface Organization {
  id: number;
  name: string;
  code: string;
  type: 'company' | 'department' | 'team' | 'group';
  parent_id?: number;
  manager_name?: string;
  manager_email?: string;
  manager_phone?: string;
  description?: string;
  sort_order: number;
  user_count?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Program {
  id: number;
  name: string;
  code: string;
  description?: string;
  category?: string;
  status: 'active' | 'inactive' | 'development';
  url?: string;
  icon?: string;
  sortOrder: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface Board {
  id: number;
  name: string;
  description?: string;
  category?: string;
  type?: string;
  slug?: string;
  sort_order: number;
  is_active: boolean;
  post_count?: number;
  view_count?: number;
  allow_anonymous?: boolean;
  require_approval?: boolean;
  allow_comments?: boolean;
  allow_attachments?: boolean;
  max_file_size?: number;
  posts_per_page?: number;
  created_at: string;
  updated_at: string;
}

export interface Menu {
  id: number;
  name: string;
  display_name?: string;
  path?: string;
  icon?: string;
  parent_id?: number;
  sort_order: number;
  is_active: boolean;
  is_visible: boolean;
  requires_auth: boolean;
  is_external: boolean;
  menu_type?: string;
  component?: string;
  description?: string;
  required_permissions?: Permission[];
  children?: Menu[];
  created_at: string;
  updated_at: string;
}

export interface Notice {
  id: number;
  title: string;
  content: string;
  type: 'info' | 'warning' | 'error' | 'success';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  category?: string;
  is_urgent?: boolean;
  is_pinned?: boolean;
  allow_comments?: boolean;
  send_notification?: boolean;
  target_type?: 'all' | 'specific' | 'admin';
  target_groups?: string[];
  status: 'draft' | 'published' | 'archived' | 'expired' | 'unpublished';
  author: { id: number; name: string; avatar?: string };
  publish_date: string;
  view_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}