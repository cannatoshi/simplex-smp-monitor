/**
 * SimpleX SMP Monitor - Chutney API Client
 * Private Tor Network Management
 * 
 * v0.1.14-alpha
 */

const API_BASE = '/api/v1';

// =============================================================================
// BASE FETCH HELPER
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
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      } else if (errorData.error) {
        errorMessage = errorData.error;
      } else if (typeof errorData === 'object') {
        errorMessage = Object.entries(errorData)
          .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
          .join('; ');
      }
    } catch {
      // Could not parse JSON
    }
    throw new Error(errorMessage);
  }
  
  const text = await response.text();
  if (!text) return {} as T;
  return JSON.parse(text);
}

// =============================================================================
// TOR NETWORK TYPES
// =============================================================================

export type NetworkStatus = 
  | 'not_created' 
  | 'created'
  | 'creating' 
  | 'bootstrapping' 
  | 'running' 
  | 'stopping' 
  | 'stopped' 
  | 'error';

export type NetworkTemplate = 
  | 'minimal' 
  | 'basic' 
  | 'standard' 
  | 'forensic' 
  | 'custom';

export type NodeType = 'da' | 'guard' | 'middle' | 'exit' | 'client' | 'hs';

export type NodeStatus = 
  | 'not_created' 
  | 'created' 
  | 'starting' 
  | 'bootstrapping' 
  | 'running' 
  | 'stopping' 
  | 'stopped' 
  | 'error';

export type CaptureStatus = 
  | 'recording' 
  | 'completed' 
  | 'analyzing' 
  | 'analyzed' 
  | 'error' 
  | 'deleted';

export type CircuitEventType = 'launched' | 'built' | 'extended' | 'failed' | 'closed';

// =============================================================================
// TOR NETWORK INTERFACE
// =============================================================================

export interface TorNetwork {
  id: string;
  name: string;
  slug: string;
  description: string;
  
  // Template & Node Counts
  template: NetworkTemplate;
  num_directory_authorities: number;
  num_guard_relays: number;
  num_middle_relays: number;
  num_exit_relays: number;
  num_clients: number;
  num_hidden_services: number;
  
  // Port Configuration
  base_control_port: number;
  base_socks_port: number;
  base_or_port: number;
  base_dir_port: number;
  
  // Tor Options
  testing_tor_network: boolean;
  voting_interval: number;
  assume_reachable: boolean;
  
  // Traffic Capture
  capture_enabled: boolean;
  capture_filter: string;
  max_capture_size_mb: number;
  capture_rotate_interval: number;
  
  // Docker
  docker_network_name: string;
  container_prefix: string;
  
  // Status
  status: NetworkStatus;
  status_display: string;
  status_message: string;
  bootstrap_progress: number;
  
  // Consensus
  consensus_valid: boolean;
  consensus_valid_after: string | null;
  consensus_fresh_until: string | null;
  consensus_valid_until: string | null;
  
  // Statistics
  total_circuits_created: number;
  total_bytes_transferred: number;
  total_cells_processed: number;
  
  // Computed
  total_nodes: number;
  running_nodes_count: number;
  is_running: boolean;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  started_at: string | null;
  stopped_at: string | null;
  
  // Nested nodes (from detail endpoint)
  nodes?: TorNode[];
}

// =============================================================================
// TOR NODE INTERFACE
// =============================================================================

export interface TorNode {
  id: string;
  network: string;
  name: string;
  node_type: NodeType;
  node_type_icon: string;
  index: number;
  
  // Docker
  container_id: string;
  container_name: string;
  
  // Ports
  control_port: number | null;
  socks_port: number | null;
  or_port: number | null;
  dir_port: number | null;
  
  // Identity
  fingerprint: string;
  v3_identity: string;
  nickname: string;
  onion_address: string;
  
  // Hidden Service
  hs_port: number | null;
  hs_target_port: number | null;
  
  // Flags
  flags: string[];
  
  // Status
  status: NodeStatus;
  status_display: string;
  status_message: string;
  bootstrap_progress: number;
  is_running: boolean;
  is_relay: boolean;
  
  // Traffic Capture
  capture_enabled: boolean;
  capture_interface: string;
  capture_file_path: string;
  
  // Statistics
  bytes_read: number;
  bytes_written: number;
  total_bandwidth: number;
  circuits_created: number;
  circuits_active: number;
  bandwidth_rate: number;
  bandwidth_burst: number;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  started_at: string | null;
  last_seen: string | null;
  
  // Nested
  captures?: TrafficCapture[];
  network_name?: string;
}

// =============================================================================
// TRAFFIC CAPTURE INTERFACE
// =============================================================================

export interface TrafficCapture {
  id: string;
  node: string;
  node_name: string;
  name: string;
  
  // Config
  capture_type: 'continuous' | 'triggered' | 'manual' | 'circuit';
  filter_expression: string;
  interface: string;
  
  // File
  file_path: string;
  file_size_bytes: number;
  file_size_mb: number;
  file_hash_sha256: string;
  
  // Time
  started_at: string;
  stopped_at: string | null;
  duration_seconds: number;
  
  // Stats
  packet_count: number;
  packets_per_second: number;
  bytes_captured: number;
  packets_dropped: number;
  unique_flows: number;
  tor_cells_detected: number;
  
  // Timing
  first_packet_time: string | null;
  last_packet_time: string | null;
  avg_inter_packet_delay_ms: number | null;
  
  // Status
  status: CaptureStatus;
  status_display: string;
  is_recording: boolean;
  
  // Analysis
  analysis_notes: string;
  related_circuit_id: string;
  
  created_at: string;
  updated_at: string;
  
  network_name?: string;
}

// =============================================================================
// CIRCUIT EVENT INTERFACE
// =============================================================================

export interface CircuitEvent {
  id: string;
  network: string;
  circuit_id: string;
  event_type: CircuitEventType;
  purpose: string;
  
  // Path
  path: Array<{
    fingerprint: string;
    nickname: string;
    ip?: string;
  }>;
  path_display: string;
  path_length: number;
  
  // Status
  status: string;
  reason: string;
  remote_reason: string;
  
  // Timing
  event_time: string;
  build_time_ms: number | null;
  
  // Source
  source_node: string | null;
  source_node_name: string;
  
  created_at: string;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

export interface TorNetworkListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TorNetwork[];
}

export interface TorNodeListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TorNode[];
}

export interface TrafficCaptureListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TrafficCapture[];
}

export interface CircuitEventListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CircuitEvent[];
}

// =============================================================================
// ACTION TYPES
// =============================================================================

export type NetworkAction = 'create' | 'start' | 'stop' | 'restart' | 'delete';
export type NodeAction = 'start' | 'stop' | 'restart' | 'delete';

export interface NetworkActionResponse {
  success: boolean;
  message: string;
  status: NetworkStatus;
  status_display: string;
}

export interface NodeActionResponse {
  success: boolean;
  message: string;
  status: NodeStatus;
  status_display: string;
}

export interface NetworkStatusDetail {
  network: {
    id: string;
    name: string;
    status: NetworkStatus;
    status_display: string;
    bootstrap_progress: number;
    consensus_valid: boolean;
  };
  nodes_by_type: Record<string, Array<{
    id: string;
    name: string;
    status: NodeStatus;
    status_display: string;
    bootstrap_progress: number;
  }>>;
  total_nodes: number;
  running_nodes: number;
}

export interface NetworkTopology {
  nodes: Array<{
    id: string;
    label: string;
    type: NodeType;
    icon: string;
    status: NodeStatus;
    group: string;
  }>;
  edges: Array<{
    from: string;
    to: string;
    type: 'consensus' | 'directory' | 'circuit';
  }>;
}

// =============================================================================
// FILTER TYPES
// =============================================================================

export interface TorNetworkFilters {
  status?: NetworkStatus;
  template?: NetworkTemplate;
}

export interface TorNodeFilters {
  network?: string;
  type?: NodeType;
  status?: NodeStatus;
}

export interface TrafficCaptureFilters {
  node?: string;
  network?: string;
  status?: CaptureStatus;
}

export interface CircuitEventFilters {
  network?: string;
  circuit_id?: string;
  event_type?: CircuitEventType;
  purpose?: string;
}

// =============================================================================
// TOR NETWORKS API
// =============================================================================

export const torNetworksApi = {
  // CRUD
  list: (filters?: TorNetworkFilters) => {
    const params = new URLSearchParams();
    if (filters?.status) params.set('status', filters.status);
    if (filters?.template) params.set('template', filters.template);
    const query = params.toString();
    return apiFetch<TorNetworkListResponse>(`/chutney/networks/${query ? `?${query}` : ''}`);
  },
  
  get: (id: string) => apiFetch<TorNetwork>(`/chutney/networks/${id}/`),
  
  create: (data: Partial<TorNetwork>) => apiFetch<TorNetwork>('/chutney/networks/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  update: (id: string, data: Partial<TorNetwork>) => apiFetch<TorNetwork>(`/chutney/networks/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  patch: (id: string, data: Partial<TorNetwork>) => apiFetch<TorNetwork>(`/chutney/networks/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  
  delete: (id: string) => apiFetch<void>(`/chutney/networks/${id}/`, { method: 'DELETE' }),
  
  // Actions
  action: (id: string, action: NetworkAction, removeVolumes = false) =>
    apiFetch<NetworkActionResponse>(`/chutney/networks/${id}/network_action/`, {
      method: 'POST',
      body: JSON.stringify({ action, remove_volumes: removeVolumes }),
    }),
  
  // Status & Topology
  statusDetail: (id: string) =>
    apiFetch<NetworkStatusDetail>(`/chutney/networks/${id}/status_detail/`),
  
  topology: (id: string) =>
    apiFetch<NetworkTopology>(`/chutney/networks/${id}/topology/`),
};

// =============================================================================
// TOR NODES API
// =============================================================================

export const torNodesApi = {
  list: (filters?: TorNodeFilters) => {
    const params = new URLSearchParams();
    if (filters?.network) params.set('network', filters.network);
    if (filters?.type) params.set('type', filters.type);
    if (filters?.status) params.set('status', filters.status);
    const query = params.toString();
    return apiFetch<TorNodeListResponse>(`/chutney/nodes/${query ? `?${query}` : ''}`);
  },
  
  get: (id: string) => apiFetch<TorNode>(`/chutney/nodes/${id}/`),
  
  action: (id: string, action: NodeAction, removeVolumes = false) =>
    apiFetch<NodeActionResponse>(`/chutney/nodes/${id}/node_action/`, {
      method: 'POST',
      body: JSON.stringify({ action, remove_volumes: removeVolumes }),
    }),
  
  logs: (id: string, tail = 100) =>
    apiFetch<{ logs: string; node_name: string; container_name: string; status: string }>(
      `/chutney/nodes/${id}/logs/?tail=${tail}`
    ),
  
  bandwidth: (id: string) =>
    apiFetch<{
      bytes_read: number;
      bytes_written: number;
      total: number;
      rate: number;
      burst: number;
      circuits_active: number;
    }>(`/chutney/nodes/${id}/bandwidth/`),
};

// =============================================================================
// TRAFFIC CAPTURES API
// =============================================================================

export const trafficCapturesApi = {
  list: (filters?: TrafficCaptureFilters) => {
    const params = new URLSearchParams();
    if (filters?.node) params.set('node', filters.node);
    if (filters?.network) params.set('network', filters.network);
    if (filters?.status) params.set('status', filters.status);
    const query = params.toString();
    return apiFetch<TrafficCaptureListResponse>(`/chutney/captures/${query ? `?${query}` : ''}`);
  },
  
  get: (id: string) => apiFetch<TrafficCapture>(`/chutney/captures/${id}/`),
  
  downloadUrl: (id: string) => `${API_BASE}/chutney/captures/${id}/download/`,
};

// =============================================================================
// CIRCUIT EVENTS API
// =============================================================================

export const circuitEventsApi = {
  list: (filters?: CircuitEventFilters) => {
    const params = new URLSearchParams();
    if (filters?.network) params.set('network', filters.network);
    if (filters?.circuit_id) params.set('circuit_id', filters.circuit_id);
    if (filters?.event_type) params.set('event_type', filters.event_type);
    if (filters?.purpose) params.set('purpose', filters.purpose);
    const query = params.toString();
    return apiFetch<CircuitEventListResponse>(`/chutney/events/${query ? `?${query}` : ''}`);
  },
  
  get: (id: string) => apiFetch<CircuitEvent>(`/chutney/events/${id}/`),
};