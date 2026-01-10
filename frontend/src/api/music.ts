/**
 * SimpleX SMP Monitor - Music API Client
 * =======================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * API client for music player endpoints.
 */

const API_BASE = '/api/v1/music';

// Types
export interface Track {
  id: string;
  title: string;
  artist: string;
  duration: number | null;
  source_type: 'youtube' | 'local';
  source_id: string;
  source_url: string;
  thumbnail_url: string;
  youtube_url: string | null;
  play_count: number;
  is_cached: boolean;
  cached_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Playlist {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string | null;
  playlist_type: 'user' | 'curated' | 'system';
  system_key: string | null;  // 'video_help' | 'news' | null
  is_system_playlist: boolean;
  is_public: boolean;
  track_count: number;
  total_duration: number;
  first_track_thumbnail: string | null;
  entries?: PlaylistEntry[];
  created_at: string;
  updated_at: string;
}

export interface PlaylistEntry {
  id: string;
  track: Track;
  position: number;
  added_at: string;
}

export interface StreamResponse {
  source: 'youtube' | 'cache';
  url: string;
  cached: boolean;
}

export interface SearchResult {
  video_id: string;
  title: string;
  artist: string;
  duration: number | null;
  thumbnail_url: string;
}

export interface CacheStatus {
  is_caching: boolean;
  active_downloads_count: number;
  active_downloads: Array<{
    id: string;
    video_id: string;
    status: string;
    started_at: string;
  }>;
  recent_failures: Array<{
    id: string;
    video_id: string;
    error_message: string;
    started_at: string;
  }>;
  stats: {
    total_downloads: number;
    completed_count: number;
    failed_count: number;
    success_rate: number;
    cache_size: {
      total_mb: number;
      file_count: number;
      max_mb: number;
      usage_percent: number;
    };
  };
}

export interface CacheSettings {
  cache_enabled: boolean;
  max_cache_size_mb: number;
  auto_cleanup_enabled: boolean;
  cleanup_after_days: number;
  max_concurrent_downloads: number;
  min_delay_between_downloads: number;
  preferred_format: string;
  preferred_bitrate: number;
}

// API Functions

export async function fetchTracks(): Promise<Track[]> {
  const response = await fetch(`${API_BASE}/tracks/`);
  if (!response.ok) throw new Error('Failed to fetch tracks');
  const data = await response.json();
  return data.results || data;
}

export async function fetchTrack(id: string): Promise<Track> {
  const response = await fetch(`${API_BASE}/tracks/${id}/`);
  if (!response.ok) throw new Error('Failed to fetch track');
  return response.json();
}

export async function getStreamUrl(trackId: string): Promise<StreamResponse> {
  const response = await fetch(`${API_BASE}/tracks/${trackId}/stream/`);
  if (!response.ok) throw new Error('Failed to get stream URL');
  return response.json();
}

export async function searchYouTube(query: string, limit = 10): Promise<SearchResult[]> {
  const response = await fetch(
    `${API_BASE}/tracks/search/?q=${encodeURIComponent(query)}&limit=${limit}`
  );
  if (!response.ok) throw new Error('Search failed');
  const data = await response.json();
  return data.results;
}

export async function addTrackFromYouTube(
  urlOrId: string,
  autoCache = false
): Promise<{ status: string; track: Track }> {
  const response = await fetch(`${API_BASE}/tracks/add_from_youtube/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url_or_id: urlOrId, auto_cache: autoCache }),
  });
  if (!response.ok) throw new Error('Failed to add track');
  return response.json();
}

export async function cacheTrack(trackId: string): Promise<{ status: string; log_id: string }> {
  const response = await fetch(`${API_BASE}/tracks/${trackId}/cache/`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to start caching');
  return response.json();
}

export async function deleteTrack(trackId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/tracks/${trackId}/`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete track');
}

// Playlists

export async function fetchPlaylists(): Promise<Playlist[]> {
  const response = await fetch(`${API_BASE}/playlists/`);
  if (!response.ok) throw new Error('Failed to fetch playlists');
  const data = await response.json();
  return data.results || data;
}

export async function fetchPlaylist(id: string): Promise<Playlist> {
  const response = await fetch(`${API_BASE}/playlists/${id}/`);
  if (!response.ok) throw new Error('Failed to fetch playlist');
  return response.json();
}

export async function createPlaylist(
  name: string,
  description = '',
  playlistType = 'user'
): Promise<Playlist> {
  const response = await fetch(`${API_BASE}/playlists/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description, playlist_type: playlistType }),
  });
  if (!response.ok) throw new Error('Failed to create playlist');
  return response.json();
}

export async function updatePlaylist(
  playlistId: string,
  data: { name?: string; description?: string }
): Promise<Playlist> {
  const response = await fetch(`${API_BASE}/playlists/${playlistId}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update playlist');
  return response.json();
}

export async function addTrackToPlaylist(
  playlistId: string,
  trackId: string
): Promise<PlaylistEntry> {
  const response = await fetch(`${API_BASE}/playlists/${playlistId}/add_track/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ track_id: trackId }),
  });
  if (!response.ok) throw new Error('Failed to add track to playlist');
  const data = await response.json();
  return data.entry;
}

export async function removeTrackFromPlaylist(
  playlistId: string,
  entryId: string
): Promise<void> {
  const response = await fetch(`${API_BASE}/playlists/${playlistId}/remove_track/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entry_id: entryId }),
  });
  if (!response.ok) throw new Error('Failed to remove track');
}

export async function deletePlaylist(playlistId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/playlists/${playlistId}/`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete playlist');
}

// Cache

export async function fetchCacheStatus(): Promise<CacheStatus> {
  const response = await fetch(`${API_BASE}/cache/status/`);
  if (!response.ok) throw new Error('Failed to fetch cache status');
  return response.json();
}

export async function fetchCacheSettings(): Promise<CacheSettings> {
  const response = await fetch(`${API_BASE}/cache/settings/`);
  if (!response.ok) throw new Error('Failed to fetch cache settings');
  return response.json();
}

export async function updateCacheSettings(
  settings: Partial<CacheSettings>
): Promise<CacheSettings> {
  const response = await fetch(`${API_BASE}/cache/settings/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!response.ok) throw new Error('Failed to update cache settings');
  return response.json();
}

export async function cacheControl(
  action: 'cleanup' | 'toggle' | 'clear_all' | 'cancel_active',
  confirm = false
): Promise<{ action: string; [key: string]: unknown }> {
  const response = await fetch(`${API_BASE}/cache/control/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, confirm }),
  });
  if (!response.ok) throw new Error('Cache control action failed');
  return response.json();
}

// Latency Correlation

export async function checkLatencyCorrelation(
  startTime: string,
  endTime: string
): Promise<{
  downloads_found: number;
  downloads: Array<{
    id: string;
    video_id: string;
    status: string;
    started_at: string;
    completed_at: string | null;
  }>;
  network_impact: boolean;
}> {
  const response = await fetch(
    `${API_BASE}/cache/correlation/?start=${encodeURIComponent(startTime)}&end=${encodeURIComponent(endTime)}`
  );
  if (!response.ok) throw new Error('Failed to check correlation');
  return response.json();
}