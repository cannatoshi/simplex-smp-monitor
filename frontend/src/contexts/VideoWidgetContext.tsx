/**
 * SimpleX SMP Monitor - Video Widget Context
 * ===========================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * Global context for the floating video widget.
 */
import { createContext, useContext, useState, ReactNode } from 'react';

interface VideoWidgetState {
  isOpen: boolean;
  videoId: string | null;
  title: string;
}

interface VideoWidgetContextType {
  widget: VideoWidgetState;
  openVideo: (videoId: string, title: string) => void;
  closeVideo: () => void;
}

const VideoWidgetContext = createContext<VideoWidgetContextType | null>(null);

export function VideoWidgetProvider({ children }: { children: ReactNode }) {
  const [widget, setWidget] = useState<VideoWidgetState>({
    isOpen: false,
    videoId: null,
    title: '',
  });

  const openVideo = (videoId: string, title: string) => {
    setWidget({
      isOpen: true,
      videoId,
      title,
    });
  };

  const closeVideo = () => {
    setWidget({
      isOpen: false,
      videoId: null,
      title: '',
    });
  };

  return (
    <VideoWidgetContext.Provider value={{ widget, openVideo, closeVideo }}>
      {children}
    </VideoWidgetContext.Provider>
  );
}

export function useVideoWidget() {
  const context = useContext(VideoWidgetContext);
  if (!context) {
    throw new Error('useVideoWidget must be used within VideoWidgetProvider');
  }
  return context;
}