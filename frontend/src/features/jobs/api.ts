import apiClient from '@/lib/apiClient';

export interface Job {
  id: string;
  title: string;
  description: string;
  department?: string;
  location?: string;
  type?: string;
  status: string;
}

export interface Match {
  id: string;
  candidate_id: string;
  job_id: string;
  final_score: number;
  score_components: {
    cross_encoder_score?: number;
    skill_match_score?: number;
    experience_score?: number;
    behavior_score?: number;
  };
  flags: string[];
  explanation?: any;
}

export const jobsApi = {
  getJobs: async (): Promise<Job[]> => {
    const response = await apiClient.get<Job[]>('/jobs/');
    return response.data;
  },

  getJob: async (id: string): Promise<Job> => {
    const response = await apiClient.get<Job>(`/jobs/${id}`);
    return response.data;
  },

  createJob: async (data: Partial<Job>): Promise<Job> => {
    const response = await apiClient.post<Job>('/jobs/', data);
    return response.data;
  },

  rankCandidates: async (jobId: string): Promise<{status: string, message: string}> => {
    const response = await apiClient.post(`/jobs/${jobId}/rank`);
    return response.data;
  },

  getMatches: async (jobId: string): Promise<Match[]> => {
    const response = await apiClient.get<Match[]>(`/jobs/${jobId}/matches`);
    return response.data;
  },
};
