import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesApi, Candidate } from './api';

export const useCandidates = () => {
  return useQuery({
    queryKey: ['candidates'],
    queryFn: candidatesApi.getCandidates,
  });
};

export const useCandidate = (id: string | null) => {
  return useQuery({
    queryKey: ['candidate', id],
    queryFn: () => candidatesApi.getCandidateById(id as string),
    enabled: !!id,
  });
};

export const useUploadResume = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { file: File; name: string; email: string; onProgress?: (p: any) => void }) => 
      candidatesApi.uploadResume(data.file, data.name, data.email, data.onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
    }
  });
};


