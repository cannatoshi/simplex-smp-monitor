/**
 * SimpleX SMP Monitor - API Client
 */
const API_BASE = '/api/v1';

// =============================================================================
// Base Fetch Helper
// =============================================================================
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  
  const text = await response.text();
  if (!text) return {} as T;
  return JSON.parse(text);
}

// =============================================================================
// Types
// =============================================================================
export interface DashboardStats {
  total_servers: number;
  active_servers: number;
  online_servers: number;
  offline_servers: number;
  smp_servers: number;
  xftp_servers: number;
  onion_servers: number;
  total_tests: number;
  active_tests: number;
  running_tests: number;
  total_clients: number;
  running_clients: number;
  total_events: number;
  error_events_24h: number;
  avg_latency: number | null;
  overall_uptime: number | null;
}

export interface ActivityData {
  hour: string;
  checks: number;
  online: number;
  offline: number;
  avg_latency: number | null;
}

export interface LatencyData {
  server_id: number;
  server_name: string;
  avg_latency: number | null;
  min_latency: number | null;
  max_latency: number | null;
  last_latency: number | null;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  color: string;
  icon: string;
  sort_order: number;
  server_count: number;
  online_server_count: number;
  created_at: string;
  updated_at: string;
}

export interface Server {
  id: number;
  name: string;
  server_type: 'smp' | 'xftp';
  address?: string;
  host: string;
  fingerprint: string;
  password?: string;
  description?: string;
  location?: string;
  is_active: boolean;
  maintenance_mode: boolean;
  last_status: 'online' | 'offline' | 'error' | 'unknown' | null;
  last_latency: number | null;
  last_check: string | null;
  last_error?: string;
  is_onion: boolean;
  uptime_percent: number | null;
  categories: Category[];
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Test {
  id: number;
  name: string;
  test_type: string;
  is_active: boolean;
  status: string;
  last_run: string | null;
  created_at: string;
  server_count?: number;
  success_rate?: number;
}

export interface Event {
  id: number;
  event_type: string;
  severity: string;
  level: string;
  source: string;
  message: string;
  server_name?: string;
  created_at: string;
}

export interface ServerFilters {
  type?: 'smp' | 'xftp';
  status?: string;
  active?: boolean;
  maintenance?: boolean;
  category?: number;
  onion?: boolean;
}

export interface ServerListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Server[];
}

export interface CategoryListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Category[];
}

export interface TestListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Test[];
}

export interface EventListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Event[];
}

// =============================================================================
// Client Types (SimpleX CLI Clients)
// =============================================================================
export interface SimplexClient {
  id: string;
  name: string;
  slug: string;
  profile_name: string;
  description: string;
  websocket_port: number;
  status: 'created' | 'starting' | 'running' | 'stopping' | 'stopped' | 'error';
  status_display: string;
  use_tor: boolean;
  messages_sent: number;
  messages_received: number;
  messages_failed: number;
  connection_count: number;
  uptime_display: string | null;
  delivery_success_rate: number;
  created_at: string;
  last_active_at: string | null;
  started_at: string | null;
  last_error?: string;
  container_id?: string;
  container_name?: string;
  data_volume?: string;
  avg_latency_ms?: number | null;
  min_latency_ms?: number | null;
  max_latency_ms?: number | null;
  messages_delivered?: number;
  smp_server_ids?: number[];
}

// Alias for backwards compatibility
export type Client = SimplexClient;

export interface ClientConnection {
  id: string;
  client_a: string;
  client_b: string;
  client_a_name: string;
  client_b_name: string;
  client_a_slug: string;
  client_b_slug: string;
  contact_name_on_a: string;
  contact_name_on_b: string;
  status: 'pending' | 'connecting' | 'connected' | 'failed' | 'deleted';
  status_display: string;
  created_at: string;
  connected_at: string | null;
}

export interface ClientStats {
  total: number;
  running: number;
  stopped: number;
  error: number;
  total_messages_sent: number;
  total_messages_received: number;
  available_ports: number[];
}

export interface ClientListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: SimplexClient[];
}

// =============================================================================
// Dashboard API
// =============================================================================
export const dashboardApi = {
  getStats: () => apiFetch<DashboardStats>('/dashboard/stats/'),
  getActivity: (hours = 24) => apiFetch<ActivityData[]>(`/dashboard/activity/?hours=${hours}`),
  getLatency: (hours = 24) => apiFetch<LatencyData[]>(`/dashboard/latency/?hours=${hours}`),
  getRecentServers: (limit = 10) => apiFetch<Server[]>(`/dashboard/servers/?limit=${limit}`),
  getRecentTests: (limit = 10) => apiFetch<Test[]>(`/dashboard/tests/?limit=${limit}`),
  getRecentEvents: (limit = 10) => apiFetch<Event[]>(`/dashboard/events/?limit=${limit}`),
};

// =============================================================================
// Servers API
// =============================================================================
export const serversApi = {
  list: (filters?: ServerFilters) => {
    const params = new URLSearchParams();
    if (filters?.type) params.set('type', filters.type);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.active !== undefined) params.set('active', String(filters.active));
    if (filters?.maintenance !== undefined) params.set('maintenance', String(filters.maintenance));
    if (filters?.category) params.set('category', String(filters.category));
    if (filters?.onion) params.set('onion', String(filters.onion));
    const query = params.toString();
    return apiFetch<ServerListResponse>(`/servers/${query ? `?${query}` : ''}`);
  },
  
  get: (id: number) => apiFetch<Server>(`/servers/${id}/`),
  
  create: (data: Partial<Server>) => apiFetch<Server>('/servers/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  update: (id: number, data: Partial<Server>) => apiFetch<Server>(`/servers/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  delete: (id: number) => apiFetch<void>(`/servers/${id}/`, { method: 'DELETE' }),
  
  test: (id: number) => apiFetch<{ status: string; message: string }>(`/servers/${id}/test/`, { method: 'POST' }),
  
  toggleActive: (id: number) => apiFetch<{ id: number; is_active: boolean }>(`/servers/${id}/toggle_active/`, { method: 'POST' }),
  
  toggleMaintenance: (id: number) => apiFetch<{ id: number; maintenance_mode: boolean }>(`/servers/${id}/toggle_maintenance/`, { method: 'POST' }),
};

// =============================================================================
// Categories API
// =============================================================================
export const categoriesApi = {
  list: () => apiFetch<CategoryListResponse>('/categories/'),
  get: (id: number) => apiFetch<Category>(`/categories/${id}/`),
  create: (data: Partial<Category>) => apiFetch<Category>('/categories/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id: number, data: Partial<Category>) => apiFetch<Category>(`/categories/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiFetch<void>(`/categories/${id}/`, { method: 'DELETE' }),
};

// =============================================================================
// Tests API
// =============================================================================
export const testsApi = {
  list: () => apiFetch<TestListResponse>('/stresstests/'),
  get: (id: number) => apiFetch<Test>(`/stresstests/${id}/`),
};

// =============================================================================
// Events API
// =============================================================================
export const eventsApi = {
  list: (limit = 50) => apiFetch<EventListResponse>(`/events/?limit=${limit}`),
};

// =============================================================================
// Clients API (legacy - for useApi hooks)
// =============================================================================
export const clientsApi = {
  list: (status?: string) => {
    const params = status ? `?status=${status}` : '';
    return apiFetch<ClientListResponse>(`/clients/${params}`);
  },
  get: (id: string) => apiFetch<SimplexClient>(`/clients/${id}/`),
};

// =============================================================================
// SimpleX Clients API (full featured)
// =============================================================================
export const simplexClientsApi = {
  list: (status?: string) => {
    const params = status ? `?status=${status}` : '';
    return apiFetch<ClientListResponse>(`/clients/${params}`);
  },
  
  get: (id: string) => apiFetch<SimplexClient>(`/clients/${id}/`),
  
  create: (data: Partial<SimplexClient>) => apiFetch<SimplexClient>('/clients/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  update: (id: string, data: Partial<SimplexClient>) => apiFetch<SimplexClient>(`/clients/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  delete: (id: string) => apiFetch<void>(`/clients/${id}/`, { method: 'DELETE' }),
  
  start: (id: string) => apiFetch<{ success: boolean; status: string; message: string }>(`/clients/${id}/start/`, { method: 'POST' }),
  
  stop: (id: string) => apiFetch<{ success: boolean; status: string; message: string }>(`/clients/${id}/stop/`, { method: 'POST' }),
  
  restart: (id: string) => apiFetch<{ success: boolean; status: string; message: string }>(`/clients/${id}/restart/`, { method: 'POST' }),
  
  logs: (id: string, tail = 50) => apiFetch<{ logs: string; status: string }>(`/clients/${id}/logs/?tail=${tail}`),
  
  connections: (id: string) => apiFetch<ClientConnection[]>(`/clients/${id}/connections/`),
  
  stats: () => apiFetch<ClientStats>('/clients-stats/'),
};

// Messages API
export interface TestMessage {
  direction?: 'sent' | 'received';
  id: string;
  sender: number;
  recipient: number;
  sender_name: string;
  recipient_name: string;
  content: string;
  delivery_status: 'pending' | 'sent' | 'delivered' | 'failed';
  status_display: string;
  total_latency_ms: number | null;
  created_at: string;
}

export const messagesApi = {
  list: (clientId?: string | number, direction?: 'sent' | 'received') => {
    let url = '/messages/';
    const params = new URLSearchParams();
    if (clientId) params.append('client', String(clientId));
    if (direction) params.append('direction', direction);
    if (params.toString()) url += '?' + params.toString();
    return apiFetch<{ results: TestMessage[] } | TestMessage[]>(url).then(r => Array.isArray(r) ? r : r.results);
  },
};
