// Server Types
export interface Category {
  id: number
  name: string
  description: string
  color: string
  icon: string
  server_count: number
  active_server_count: number
  online_server_count: number
}

export interface Server {
  id: number
  name: string
  server_type: 'smp' | 'xftp'
  address: string
  description: string
  location: string
  
  // Status
  is_active: boolean
  maintenance_mode: boolean
  last_check: string | null
  last_status: 'unknown' | 'online' | 'offline' | 'error'
  last_latency: number | null
  last_error: string
  
  // Config
  custom_timeout: number | null
  priority: number
  expected_uptime: number
  max_latency: number
  
  // Stats
  total_checks: number
  successful_checks: number
  avg_latency: number | null
  
  // Computed
  host: string
  fingerprint: string
  password: string
  is_onion: boolean
  uptime_percent: number | null
  is_below_sla: boolean
  
  // Relations
  categories: Category[]
  
  // Timestamps
  created_at: string
  updated_at: string
}

export interface TestRun {
  id: number
  name: string
  test_type: 'monitoring' | 'stress' | 'latency'
  status: 'active' | 'paused' | 'completed' | 'running'
  interval_seconds: number
  created_at: string
  total_checks: number
  successful_checks: number
  success_rate?: number
  last_run?: string
}

export interface Event {
  id: number
  event_type: 'success' | 'warning' | 'error' | 'info'
  level: 'INFO' | 'WARNING' | 'ERROR'
  message: string
  source: string
  timestamp: string
  created_at: string
  server?: Server
}

export interface Client {
  id: number
  name: string
  description: string
  status: 'running' | 'stopped' | 'error'
  started_at: string | null
}

// API Response types
export interface DashboardStats {
  server_count: number
  active_servers: number
  running_tests: number
  total_tests: number
}

export interface ConnectionTestResult {
  success: boolean
  message: string
  latency?: number
  used_tor?: boolean
}
