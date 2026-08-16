import { useQuery } from '@tanstack/react-query';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface PipelineStatus {
  status: string;
  models_loaded: string[];
  [key: string]: unknown;
}

async function fetchPipelineStatus(): Promise<PipelineStatus> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Pipeline health check failed: ${response.status}`);
  }

  const data = await response.json();

  return {
    status: data.status || 'unknown',
    models_loaded: Array.isArray(data.models_loaded)
      ? data.models_loaded
      : [],
    ...data,
  };
}

export function usePipelineStatus() {
  return useQuery<PipelineStatus>({
    queryKey: ['pipeline-status'],
    queryFn: fetchPipelineStatus,
    refetchInterval: 30000,
    staleTime: 10000,
  });
}