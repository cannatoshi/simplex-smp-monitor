/**
 * SimpleX SMP Monitor - Cache Forensics API
 * ==========================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * API client for cache forensics endpoints.
 */

const API_BASE = '/api/v1/music';

// Types
export interface CacheLogEntry {
  id: string;
  video_id: string;
  status: 'started' | 'downloading' | 'converting' | 'completed' | 'failed' | 'cached' | 'cancelled';
  is_active: boolean;
  started_at: string;
  completed_at: string | null;
  duration: number | null;
  file_size_bytes: number | null;
  download_duration_seconds: number | null;
  bandwidth_bytes_per_sec: number | null;
  error_message: string;
  error_code: string;
  retry_count: number;
  audio_format: string;
  audio_bitrate: number | null;
}

export interface CacheHistoryResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CacheLogEntry[];
}

export interface DownloadPerDay {
  date: string;
  total: number;
  completed: number;
  failed: number;
  total_bytes: number | null;
  total_mb: number;
}

export interface BandwidthPoint {
  hour: string;
  avg_bandwidth: number | null;
  max_bandwidth: number | null;
  download_count: number;
  avg_bandwidth_kbps: number;
  max_bandwidth_kbps: number;
}

export interface HeatmapCell {
  hour: number;
  weekday: number;  // 1=Sunday, 7=Saturday
  count: number;
}

export interface SizeDistribution {
  range: string;
  count: number;
}

export interface TopError {
  error_message: string;
  count: number;
}

export interface CacheAnalytics {
  period_days: number;
  generated_at: string;
  
  summary: {
    total_downloads: number;
    completed: number;
    failed: number;
    success_rate: number;
    total_bytes: number;
    total_mb: number;
    total_gb: number;
    avg_bandwidth_kbps: number;
    max_bandwidth_kbps: number;
    avg_duration_seconds: number;
    total_duration_minutes: number;
  };
  
  last_24h: {
    total: number;
    completed: number;
    failed: number;
    total_mb: number;
  };
  
  downloads_per_day: DownloadPerDay[];
  bandwidth_timeline: BandwidthPoint[];
  heatmap: HeatmapCell[];
  size_distribution: SizeDistribution[];
  top_errors: TopError[];
}

export interface CorrelationResult {
  start: string;
  end: string;
  downloads_found: number;
  downloads: CacheLogEntry[];
  network_impact: boolean;
}

// API Functions

export async function fetchCacheHistory(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  days?: number;
  order?: string;
}): Promise<CacheHistoryResponse> {
  const searchParams = new URLSearchParams();
  
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
  if (params?.status) searchParams.set('status', params.status);
  if (params?.days) searchParams.set('days', params.days.toString());
  if (params?.order) searchParams.set('order', params.order);
  
  const url = `${API_BASE}/cache/history/?${searchParams.toString()}`;
  const response = await fetch(url);
  
  if (!response.ok) throw new Error('Failed to fetch cache history');
  return response.json();
}

export async function fetchCacheAnalytics(days: number = 30): Promise<CacheAnalytics> {
  const response = await fetch(`${API_BASE}/cache/analytics/?days=${days}`);
  
  if (!response.ok) throw new Error('Failed to fetch cache analytics');
  return response.json();
}

export async function cleanupCacheHistory(days: number): Promise<{ deleted_count: number; cutoff_date: string }> {
  const response = await fetch(`${API_BASE}/cache/history/cleanup/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ days, confirm: true }),
  });
  
  if (!response.ok) throw new Error('Failed to cleanup cache history');
  return response.json();
}

export async function fetchCorrelation(start: string, end: string): Promise<CorrelationResult> {
  const response = await fetch(
    `${API_BASE}/cache/correlation/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`
  );
  
  if (!response.ok) throw new Error('Failed to fetch correlation');
  return response.json();
}

export async function clearAllCache(): Promise<{ deleted_count: number; freed_bytes: number }> {
  const response = await fetch(`${API_BASE}/cache/control/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'clear_all', confirm: true }),
  });
  
  if (!response.ok) throw new Error('Failed to clear cache');
  return response.json();
}

export async function cancelActiveDownloads(): Promise<{ cancelled_count: number }> {
  const response = await fetch(`${API_BASE}/cache/control/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'cancel_active' }),
  });
  
  if (!response.ok) throw new Error('Failed to cancel downloads');
  return response.json();
}