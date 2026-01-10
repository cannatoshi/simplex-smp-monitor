/**
 * SimpleX SMP Monitor - Audio Player Store
 * =========================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * Global state management for the audio player using Zustand.
 * Uses CacheStatus type from music.ts API to ensure compatibility.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CacheStatus } from '../api/music';

// Re-export CacheStatus for components that need it
export type { CacheStatus } from '../api/music';

// Types
export interface Track {
  id: string;
  title: string;
  artist: string;
  duration: number | null;
  source_type: 'youtube' | 'local';
  source_id: string;
  thumbnail_url: string;
  youtube_url: string | null;
  is_cached: boolean;
}

export type RepeatMode = 'none' | 'one' | 'all';

// Default cache status matching API structure
const defaultCacheStatus: CacheStatus = {
  is_caching: false,
  active_downloads_count: 0,
  active_downloads: [],
  recent_failures: [],
  stats: {
    total_downloads: 0,
    completed_count: 0,
    failed_count: 0,
    success_rate: 100,
    cache_size: {
      total_mb: 0,
      file_count: 0,
      max_mb: 2000,
      usage_percent: 0,
    },
  },
};

interface AudioPlayerState {
  // Playback state
  isPlaying: boolean;
  isLoading: boolean;
  currentTrack: Track | null;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;

  // Queue
  queue: Track[];
  queueIndex: number;
  shuffleEnabled: boolean;
  repeatMode: RepeatMode;

  // UI state
  isExpanded: boolean;
  isMinimized: boolean;

  // Cache status
  cacheStatus: CacheStatus;

  // Actions - Playback
  play: () => void;
  pause: () => void;
  togglePlay: () => void;
  setTrack: (track: Track | null) => void;
  setCurrentTrack: (track: Track | null) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setIsLoading: (loading: boolean) => void;
  setIsPlaying: (playing: boolean) => void;

  // Actions - Queue
  setQueue: (tracks: Track[], startIndex?: number) => void;
  addToQueue: (track: Track) => void;
  removeFromQueue: (index: number) => void;
  clearQueue: () => void;
  nextTrack: () => void;
  prevTrack: () => void;
  skipTo: (index: number) => void;
  toggleShuffle: () => void;
  cycleRepeatMode: () => void;

  // Actions - UI
  expand: () => void;
  collapse: () => void;
  minimize: () => void;
  restore: () => void;

  // Actions - Cache
  setCacheStatus: (status: CacheStatus) => void;
  
  // Actions - Reset
  resetPlayer: () => void;
}

export const useAudioPlayerStore = create<AudioPlayerState>()(
  persist(
    (set, get) => ({
      // Initial state
      isPlaying: false,
      isLoading: false,
      currentTrack: null,
      currentTime: 0,
      duration: 0,
      volume: 0.7,
      isMuted: false,
      queue: [],
      queueIndex: 0,
      shuffleEnabled: false,
      repeatMode: 'none',
      isExpanded: false,
      isMinimized: false,
      cacheStatus: defaultCacheStatus,

      // Actions - Playback
      play: () => set({ isPlaying: true }),
      pause: () => set({ isPlaying: false }),
      togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
      setIsPlaying: (playing) => set({ isPlaying: playing }),
      
      setTrack: (track) => set({ 
        currentTrack: track, 
        currentTime: 0,
        duration: track?.duration || 0,
        isLoading: !!track 
      }),
      
      setCurrentTrack: (track) => set({ 
        currentTrack: track, 
        currentTime: 0,
        duration: track?.duration || 0,
        isLoading: !!track 
      }),
      
      setCurrentTime: (time) => set({ currentTime: time }),
      setDuration: (duration) => set({ duration }),
      setVolume: (volume) => set({ volume, isMuted: volume === 0 }),
      toggleMute: () => set((state) => ({ isMuted: !state.isMuted })),
      setIsLoading: (loading) => set({ isLoading: loading }),

      // Actions - Queue
      setQueue: (tracks, startIndex = 0) => set({
        queue: tracks,
        queueIndex: startIndex,
        currentTrack: tracks[startIndex] || null,
        isLoading: tracks.length > 0,
      }),

      addToQueue: (track) => set((state) => ({
        queue: [...state.queue, track],
      })),

      removeFromQueue: (index) => set((state) => {
        const newQueue = [...state.queue];
        newQueue.splice(index, 1);
        
        let newIndex = state.queueIndex;
        if (index < state.queueIndex) {
          newIndex--;
        } else if (index === state.queueIndex && index >= newQueue.length) {
          newIndex = Math.max(0, newQueue.length - 1);
        }

        return {
          queue: newQueue,
          queueIndex: newIndex,
          currentTrack: newQueue[newIndex] || null,
        };
      }),

      clearQueue: () => set({
        queue: [],
        queueIndex: 0,
        currentTrack: null,
        isPlaying: false,
      }),

      nextTrack: () => {
        const { queue, queueIndex, repeatMode, shuffleEnabled } = get();
        if (queue.length === 0) return;

        let nextIndex: number;

        if (shuffleEnabled) {
          const availableIndices = queue
            .map((_, i) => i)
            .filter((i) => i !== queueIndex);
          if (availableIndices.length === 0) {
            nextIndex = queueIndex;
          } else {
            nextIndex = availableIndices[Math.floor(Math.random() * availableIndices.length)];
          }
        } else if (repeatMode === 'one') {
          nextIndex = queueIndex;
        } else {
          nextIndex = queueIndex + 1;
          if (nextIndex >= queue.length) {
            nextIndex = repeatMode === 'all' ? 0 : queueIndex;
            if (repeatMode === 'none' && queueIndex === queue.length - 1) {
              set({ isPlaying: false });
              return;
            }
          }
        }

        set({
          queueIndex: nextIndex,
          currentTrack: queue[nextIndex],
          currentTime: 0,
          isLoading: true,
        });
      },

      prevTrack: () => {
        const { queue, queueIndex, currentTime } = get();
        if (queue.length === 0) return;

        if (currentTime > 3) {
          set({ currentTime: 0 });
          return;
        }

        const prevIndex = queueIndex > 0 ? queueIndex - 1 : queue.length - 1;
        set({
          queueIndex: prevIndex,
          currentTrack: queue[prevIndex],
          currentTime: 0,
          isLoading: true,
        });
      },

      skipTo: (index) => {
        const { queue } = get();
        if (index >= 0 && index < queue.length) {
          set({
            queueIndex: index,
            currentTrack: queue[index],
            currentTime: 0,
            isLoading: true,
            isPlaying: true,
          });
        }
      },

      toggleShuffle: () => set((state) => ({ shuffleEnabled: !state.shuffleEnabled })),

      cycleRepeatMode: () => set((state) => {
        const modes: RepeatMode[] = ['none', 'all', 'one'];
        const currentIndex = modes.indexOf(state.repeatMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        return { repeatMode: modes[nextIndex] };
      }),

      // Actions - UI
      expand: () => set({ isExpanded: true }),
      collapse: () => set({ isExpanded: false }),
      minimize: () => set({ isMinimized: true }),
      restore: () => set({ isMinimized: false }),

      // Actions - Cache
      setCacheStatus: (status) => set({ cacheStatus: status }),
      
      // Reset
      resetPlayer: () => set({
        isPlaying: false,
        isLoading: false,
        currentTrack: null,
        currentTime: 0,
        duration: 0,
        queue: [],
        queueIndex: 0,
      }),
    }),
    {
      name: 'smp-audio-player',
      partialize: (state) => ({
        volume: state.volume,
        isMuted: state.isMuted,
        shuffleEnabled: state.shuffleEnabled,
        repeatMode: state.repeatMode,
      }),
    }
  )
);