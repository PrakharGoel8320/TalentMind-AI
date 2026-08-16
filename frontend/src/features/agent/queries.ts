import { useMutation } from '@tanstack/react-query';
import { agentApi } from './api';

export const useRunAgent = () => {
  return useMutation({
    mutationFn: (data: { jobId: string, request: string }) => 
      agentApi.runAgent(data.jobId, data.request)
  });
};
