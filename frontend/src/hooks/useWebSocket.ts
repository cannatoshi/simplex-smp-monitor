/**
 * SimpleX SMP Monitor - WebSocket Hooks für Live Updates
 * 
 * Verbindet sich mit bestehendem Django Channels Backend:
 * - /ws/clients/ → ClientUpdateConsumer (Übersichtsseite)
 * - /ws/clients/{slug}/ → ClientDetailConsumer (Detailseite)
 */
import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Event Types (passend zu consumers.py)
// =============================================================================

export interface BridgeStatusEvent {
  type: 'bridge_status';
  connected_clients: number;
}

export interface ClientStatusEvent {
  type: 'client_status';
  client_slug: string;
  status: string;
  container_id?: string;
}

export interface ClientStatsEvent {
  type: 'client_stats';
  client_slug: string;
  messages_sent: number;
  messages_received: number;
}

export interface MessageStatusEvent {
  type: 'message_status';
  message_id: string;
  status: string;
  latency_ms?: number;
}

export interface NewMessageEvent {
  type: 'new_message';
  client_slug: string;
  sender: string;
  content: string;
  timestamp: string;
}

export interface ConnectionCreatedEvent {
  type: 'connection_created';
  client_a_slug: string;
  client_b_slug: string;
  client_a_name: string;
  client_b_name: string;
  contact_name_on_a: string;
  contact_name_on_b: string;
  status: string;
}

export interface ConnectionDeletedEvent {
  type: 'connection_deleted';
  connection_id: number;
  client_a_slug: string;
}

export type WebSocketEvent = 
  | BridgeStatusEvent 
  | ClientStatusEvent 
  | ClientStatsEvent 
  | MessageStatusEvent 
  | NewMessageEvent
  | ConnectionCreatedEvent
  | ConnectionDeletedEvent;

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

// =============================================================================
// useClientsWebSocket - für Übersichtsseite (/ws/clients/)
// =============================================================================

interface UseClientsWebSocketCallbacks {
  onClientStats?: (event: ClientStatsEvent) => void;
  onClientStatus?: (event: ClientStatusEvent) => void;
  onNewMessage?: (event: NewMessageEvent) => void;
  onMessageStatus?: (event: MessageStatusEvent) => void;
  onConnectionCreated?: (event: ConnectionCreatedEvent) => void;
  onConnectionDeleted?: (event: ConnectionDeletedEvent) => void;
}

export function useClientsWebSocket(callbacks?: UseClientsWebSocketCallbacks) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [bridgeClients, setBridgeClients] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  const callbacksRef = useRef(callbacks);
  
  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);

  const getWsUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = import.meta.env?.DEV ? '8000' : window.location.port;
    return `${protocol}//${host}:${port}/ws/clients/`;
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    setConnectionState('connecting');
    const url = getWsUrl();
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('🔌 WebSocket connected:', url);
        setConnectionState('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketEvent;
          const cb = callbacksRef.current;
          
          switch (data.type) {
            case 'bridge_status':
              setBridgeClients(data.connected_clients);
              break;
            case 'client_stats':
              cb?.onClientStats?.(data);
              break;
            case 'client_status':
              cb?.onClientStatus?.(data);
              break;
            case 'new_message':
              cb?.onNewMessage?.(data);
              break;
            case 'message_status':
              cb?.onMessageStatus?.(data);
              break;
            case 'connection_created':
              cb?.onConnectionCreated?.(data);
              break;
            case 'connection_deleted':
              cb?.onConnectionDeleted?.(data);
              break;
          }
        } catch (err) {
          console.error('WebSocket parse error:', err);
        }
      };

      ws.onerror = () => setConnectionState('error');

      ws.onclose = () => {
        setConnectionState('disconnected');
        wsRef.current = null;

        if (reconnectAttempts.current < 10) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectTimeout.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('WebSocket error:', err);
      setConnectionState('error');
    }
  }, [getWsUrl]);

  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0;
    wsRef.current?.close();
    connect();
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [connect]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  return { connectionState, bridgeClients, reconnect };
}

// =============================================================================
// useClientDetailWebSocket - für Detailseite (/ws/clients/{slug}/)
// =============================================================================

export function useClientDetailWebSocket(
  clientSlug: string | undefined,
  callbacks?: UseClientsWebSocketCallbacks
) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [bridgeClients, setBridgeClients] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  const callbacksRef = useRef(callbacks);
  
  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);

  const getWsUrl = useCallback(() => {
    if (!clientSlug) return null;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = import.meta.env?.DEV ? '8000' : window.location.port;
    return `${protocol}//${host}:${port}/ws/clients/${clientSlug}/`;
  }, [clientSlug]);

  const connect = useCallback(() => {
    const url = getWsUrl();
    if (!url || wsRef.current?.readyState === WebSocket.OPEN) return;
    
    setConnectionState('connecting');
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('🔌 WebSocket connected:', url);
        setConnectionState('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketEvent;
          const cb = callbacksRef.current;
          
          switch (data.type) {
            case 'bridge_status':
              setBridgeClients(data.connected_clients);
              break;
            case 'client_stats':
              cb?.onClientStats?.(data);
              break;
            case 'client_status':
              cb?.onClientStatus?.(data);
              break;
            case 'new_message':
              cb?.onNewMessage?.(data);
              break;
            case 'message_status':
              cb?.onMessageStatus?.(data);
              break;
            case 'connection_created':
              cb?.onConnectionCreated?.(data);
              break;
            case 'connection_deleted':
              cb?.onConnectionDeleted?.(data);
              break;
          }
        } catch (err) {
          console.error('WebSocket parse error:', err);
        }
      };

      ws.onerror = () => setConnectionState('error');

      ws.onclose = () => {
        setConnectionState('disconnected');
        wsRef.current = null;

        if (reconnectAttempts.current < 10) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectTimeout.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('WebSocket error:', err);
      setConnectionState('error');
    }
  }, [getWsUrl]);

  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0;
    wsRef.current?.close();
    connect();
  }, [connect]);

  useEffect(() => {
    if (clientSlug) {
      connect();
    }
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [clientSlug, connect]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  return { connectionState, bridgeClients, reconnect };
}
