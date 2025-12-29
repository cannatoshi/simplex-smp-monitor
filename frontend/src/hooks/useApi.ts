/**
 * SimpleX SMP Monitor - React Hooks für API
 */
import { useState, useEffect, useCallback } from 'react';
import {
  dashboardApi,
  serversApi,
  categoriesApi,
  testsApi,
  eventsApi,
  clientsApi,
  DashboardStats,
  Server,
  ServerListResponse,
  ServerFilters,
  Category,
  Test,

  Event,

  Client,

  ActivityData,
  LatencyData,
} from '../api/client';

// =============================================================================
// Generic Hook State
// =============================================================================

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// =============================================================================
// Generic useApi Hook
// =============================================================================

export function useApi<T>(fetchFn: () => Promise<T>) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await fetchFn();
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// Dashboard Hooks
// =============================================================================

export function useDashboardStats() {
  const [state, setState] = useState<UseApiState<DashboardStats>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await dashboardApi.getStats();
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useActivityData(hours = 24) {
  const [state, setState] = useState<UseApiState<ActivityData[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await dashboardApi.getActivity(hours);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [hours]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useLatencyData(hours = 24) {
  const [state, setState] = useState<UseApiState<LatencyData[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await dashboardApi.getLatency(hours);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [hours]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// Servers Hooks
// =============================================================================

export function useServers(filters?: ServerFilters) {
  const [state, setState] = useState<UseApiState<ServerListResponse>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await serversApi.list(filters);
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

export function useServer(id: number | null) {
  const [state, setState] = useState<UseApiState<Server>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await serversApi.get(id);
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

export function useCategories() {
  const [state, setState] = useState<UseApiState<Category[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const response = await categoriesApi.list();
      setState({ data: response.results, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// Tests Hooks
// =============================================================================

export function useTests() {
  const [state, setState] = useState<UseApiState<Test[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const response = await testsApi.list();
      setState({ data: response.results, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useTest(id: number | null) {
  const [state, setState] = useState<UseApiState<Test>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await testsApi.get(id);
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
// Events Hooks
// =============================================================================

export function useEvents(limit = 50) {
  const [state, setState] = useState<UseApiState<Event[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const response = await eventsApi.list(limit);
      setState({ data: response.results, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [limit]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

// =============================================================================
// Clients Hooks
// =============================================================================

export function useClients(status?: string) {
  const [state, setState] = useState<UseApiState<Client[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const response = await clientsApi.list(status);
      setState({ data: response.results, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [status]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useClient(id: string | null) {
  const [state, setState] = useState<UseApiState<Client>>({
    data: null,
    loading: !!id,
    error: null,
  });

  const refetch = useCallback(async () => {
    if (!id) return;
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await clientsApi.get(id);
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
// Recent Data Hooks (für Dashboard)
// =============================================================================

export function useRecentServers(limit = 5) {
  const [state, setState] = useState<UseApiState<Server[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await dashboardApi.getRecentServers(limit);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [limit]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useRecentTests(limit = 5) {
  const [state, setState] = useState<UseApiState<Test[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await dashboardApi.getRecentTests(limit);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [limit]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useRecentEvents(limit = 5) {
  const [state, setState] = useState<UseApiState<Event[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await dashboardApi.getRecentEvents(limit);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, [limit]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
