'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import { Search, Plus, MapPin, Users, Clock, ArrowRight, Activity, Download, FileText, Printer, Bot } from 'lucide-react';
import { motion } from 'framer-motion';
import { useJobs, useCreateJob, useRankCandidates } from '@/features/jobs/queries';
import { Job } from '@/features/jobs/api';

export default function JobsPage() {
  const router = useRouter();
  const { data: jobs, isLoading } = useJobs();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-white">Active Jobs</h1>
          <p className="mt-1 text-text-secondary">Manage your open requisitions.</p>
        </div>
        <Button leftIcon={<Plus size={16} />} onClick={() => setIsCreateModalOpen(true)}>Create Job</Button>
      </div>

      <div className="flex items-center space-x-4 border-b border-white/10 pb-4">
        <div className="w-full max-w-md">
          <Input 
            placeholder="Search jobs by title or department..." 
            leftIcon={<Search size={16} />}
          />
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, idx) => (
            <Card key={idx} className="bg-white/5 border-white/10">
              <CardContent className="p-6">
                <Skeleton className="mb-4 h-7 w-3/4" />
                <Skeleton className="mb-6 h-4 w-1/2" />
                <div className="flex gap-2">
                  <Skeleton className="h-6 w-20 rounded-full" />
                  <Skeleton className="h-6 w-20 rounded-full" />
                </div>
              </CardContent>
            </Card>
          ))
        ) : jobs?.length === 0 ? (
          <div className="col-span-full py-12 text-center text-text-secondary">
            No jobs found. Create one to get started.
          </div>
        ) : (
          jobs?.map((job, idx) => (
            <motion.div 
              key={job.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.1 }}
            >
              <JobCard 
                job={job} 
                onViewMatches={() => router.push(`/jobs/${job.id}`)} 
              />
            </motion.div>
          ))
        )}
      </div>

      {isCreateModalOpen && <CreateJobModal onClose={() => setIsCreateModalOpen(false)} />}
    </div>
  );
}

function JobCard({ job, onViewMatches }: { job: Job, onViewMatches: () => void }) {
  const { mutate: rankCandidates, isPending: isRanking } = useRankCandidates();

  return (
    <Card className="flex h-full flex-col bg-white/5 border-white/10 transition-all hover:bg-white/10">
      <CardContent className="flex flex-1 flex-col p-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-white">{job.title}</h3>
            <p className="mt-1 text-sm text-text-secondary">{job.department || 'General'}</p>
          </div>
          <span className="inline-flex items-center rounded-full bg-green-500/10 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-500/20">
            {job.status || 'Active'}
          </span>
        </div>

        <div className="mt-6 flex flex-wrap gap-4 text-sm text-text-muted">
          <div className="flex items-center gap-1.5">
            <MapPin size={14} />
            <span>{job.location || 'Remote'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Users size={14} />
            <span>{job.type || 'Full-time'}</span>
          </div>
        </div>

        <div className="mt-auto pt-6 flex items-center gap-3">
          <Button 
            variant="secondary" 
            className="flex-1"
            size="sm"
            isLoading={isRanking}
            leftIcon={!isRanking && <Activity size={14} />}
            onClick={() => rankCandidates(job.id)}
          >
            {isRanking ? 'Ranking...' : 'Rank Candidates'}
          </Button>
          <Button variant="ghost" size="sm" rightIcon={<ArrowRight size={14} />} onClick={onViewMatches}>
            View
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function CreateJobModal({ onClose }: { onClose: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const { mutate: createJob, isPending } = useCreateJob();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createJob({ title, description, status: 'Active' }, {
      onSuccess: () => onClose()
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <Card className="w-full max-w-lg border-white/10 bg-surface shadow-2xl">
        <CardContent className="p-6">
          <h2 className="mb-6 font-display text-xl font-bold text-white">Create New Job</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Job Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-text-primary">Job Description</label>
              <textarea 
                className="flex h-32 w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue focus-visible:ring-offset-2"
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-white/10">
              <Button type="button" variant="ghost" onClick={onClose} disabled={isPending}>Cancel</Button>
              <Button type="submit" isLoading={isPending}>Create</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
