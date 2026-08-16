import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi, Job } from './api';

export const useJobs = () => {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
  });
};

export const useJob = (id: string | null) => {
  return useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.getJob(id as string),
    enabled: !!id,
  });
};

export const useJobMatches = (jobId: string | null) => {
  return useQuery({
    queryKey: ['jobMatches', jobId],
    queryFn: () => jobsApi.getMatches(jobId as string),
    enabled: !!jobId,
  });
};

export const useCreateJob = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Job>) => jobsApi.createJob(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    }
  });
};

export const useRankCandidates = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (jobId: string) => jobsApi.rankCandidates(jobId),
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: ['jobMatches', jobId] });
    }
  });
};

