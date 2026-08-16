import apiClient from '@/lib/apiClient';

export interface AgentResponse {
  job_id: string;
  status: string;
  explanation: string;
  candidates: any[];
  errors: string[];
}

export const agentApi = {
  runAgent: async (jobId: string, request: string): Promise<AgentResponse> => {
    const response = await apiClient.post<AgentResponse>('/agent/run', {
      job_id: jobId,
      request: request
    });
    return response.data;
  }
};
