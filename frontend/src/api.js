/**
 * API utilities and TanStack Query hooks for Prometheus RAG
 */

import { useQuery, useMutation, QueryClient } from '@tanstack/react-query';

const API_BASE = '/api';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

/**
 * Fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Hook for RAG queries
 */
export function useRagQuery(query, lang, enabled = false) {
  return useQuery({
    queryKey: ['rag', query, lang],
    queryFn: () => fetchAPI('/rag', {
      method: 'POST',
      body: JSON.stringify({ query, lang }),
    }),
    enabled: enabled && !!query,
  });
}

/**
 * Mutation for RAG queries (for manual triggering)
 */
export function useRagMutation() {
  return useMutation({
    mutationFn: ({ query, lang }) => fetchAPI('/rag', {
      method: 'POST',
      body: JSON.stringify({ query, lang }),
    }),
  });
}

/**
 * Hook for evaluation metrics
 */
export function useEvalMetrics(enabled = false) {
  return useQuery({
    queryKey: ['eval'],
    queryFn: () => fetchAPI('/eval'),
    enabled,
  });
}

/**
 * Check backend health
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => fetch('/').then(r => r.json()),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
