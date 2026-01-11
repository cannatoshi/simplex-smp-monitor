/**
 * SimpleX SMP Monitor - Chutney React Hooks
 * Private Tor Network Management
 */
import { useState, useEffect, useCallback } from 'react';
import {
  torNetworksApi,
  torNodesApi,
  trafficCapturesApi,
  circuitEventsApi,
  TorNetwork,
  TorNetworkListResponse,
  TorNetworkFilters,
  TorNode,
  TorNodeListResponse,
  TorNodeFilters,
  TrafficCapture,
  TrafficCaptureListResponse,
  TrafficCaptureFilters,
  CircuitEvent,
  CircuitEventListResponse,
  CircuitEventFilters,
  NetworkStatusDetail,
  NetworkTopology,
} from '../api/chutney';

// =============================================================================
// Generic Hook State
// =============================================================================

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// =============================================================================
// TOR NETWORKS HOOKS
// =============================================================================

export function useTorNetworks(filters?: TorNetworkFilters) {
  const [state, setState] = useState<UseApiState<TorNetworkListResponse>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await torNetworksApi.list(filters);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useTorNetwork(id: string | null) {
  const [state, setState] = useState<UseApiState<TorNetwork>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await torNetworksApi.get(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [id]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useTorNetworkStatus(id: string | null) {
  const [state, setState] = useState<UseApiState<NetworkStatusDetail>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await torNetworksApi.statusDetail(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [id]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useTorNetworkTopology(id: string | null) {
  const [state, setState] = useState<UseApiState<NetworkTopology>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await torNetworksApi.topology(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [id]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// TOR NODES HOOKS
// =============================================================================

export function useTorNodes(filters?: TorNodeFilters) {
  const [state, setState] = useState<UseApiState<TorNodeListResponse>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await torNodesApi.list(filters);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useTorNode(id: string | null) {
  const [state, setState] = useState<UseApiState<TorNode>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await torNodesApi.get(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [id]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// TRAFFIC CAPTURES HOOKS
// =============================================================================

export function useTrafficCaptures(filters?: TrafficCaptureFilters) {
  const [state, setState] = useState<UseApiState<TrafficCaptureListResponse>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await trafficCapturesApi.list(filters);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useTrafficCapture(id: string | null) {
  const [state, setState] = useState<UseApiState<TrafficCapture>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await trafficCapturesApi.get(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [id]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// CIRCUIT EVENTS HOOKS
// =============================================================================

export function useCircuitEvents(filters?: CircuitEventFilters) {
  const [state, setState] = useState<UseApiState<CircuitEventListResponse>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await circuitEventsApi.list(filters);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useCircuitEvent(id: string | null) {
  const [state, setState] = useState<UseApiState<CircuitEvent>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await circuitEventsApi.get(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [id]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// POLLING HOOK FOR LIVE UPDATES
// =============================================================================

export function useTorNetworkPolling(id: string | null, interval = 5000) {
  const [state, setState] = useState<UseApiState<NetworkStatusDetail>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    try {
      const data = await torNetworksApi.statusDetail(id);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState(s => ({ ...s, loading: false, error: (err as Error).message }));
    }
  }, [id]);

  useEffect(() => {
    if (!id) return;
    
    // Initial fetch
    refetch();
    
    // Polling
    const timer = setInterval(refetch, interval);
    
    return () => clearInterval(timer);
  }, [id, interval, refetch]);

  return { ...state, refetch };
}