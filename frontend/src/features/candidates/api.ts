import apiClient from '@/lib/apiClient';

export interface Candidate {
  id: string;
  name: string;
  email: string;
  role?: string;
  experience?: number;
  skills?: string[];
  status?: string;
  profile_jsonb?: {
    role?: string;
    skills?: string[];
    experience_years?: number;
    [key: string]: any;
  };
}

export const candidatesApi = {
  uploadResume: async (
    file: File,
    name: string,
    email: string,
    onProgress?: (progressEvent: any) => void
  ): Promise<Candidate> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    formData.append('email', email);

    const response = await apiClient.post<Candidate>('/candidates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });
    return response.data;
  },

  getCandidates: async (): Promise<Candidate[]> => {
    const response = await apiClient.get<Candidate[]>('/candidates');
    return response.data;
  },

  getCandidateById: async (id: string): Promise<Candidate> => {
    const response = await apiClient.get<Candidate>(`/candidates/${id}`);
    return response.data;
  }
};
