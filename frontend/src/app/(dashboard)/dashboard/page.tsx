'use client';
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { Activity, Database, Server, Cpu, Users, Briefcase } from 'lucide-react';
import { usePipelineStatus } from '@/features/dashboard/queries';
import { useJobs } from '@/features/jobs/queries';
import { useCandidates } from '@/features/candidates/queries';
import { motion } from 'framer-motion';
import { TiltCard } from '@/components/ui/TiltCard';
import { AnimatedBackground } from '@/components/ui/AnimatedBackground';

export default function DashboardHomePage() {
  const { data: pipelineStatus, isLoading: isPipelineLoading } = usePipelineStatus();
  const { data: jobs, isLoading: isJobsLoading } = useJobs();
  const { data: candidates, isLoading: isCandidatesLoading } = useCandidates();
  
  const isLoading = isPipelineLoading || isJobsLoading || isCandidatesLoading;

  const statCards = [
    { title: 'Pipeline Status', value: pipelineStatus?.status || 'Unknown', icon: <Activity size={24} className="text-blue-400" />, trend: pipelineStatus?.status === 'online' ? 'All systems go' : 'Degraded' },
    { title: 'Total Candidates', value: candidates?.length || 0, icon: <Users size={24} className="text-purple-400" />, trend: 'System database' },
    { title: 'Active Jobs', value: jobs?.length || 0, icon: <Briefcase size={24} className="text-green-400" />, trend: 'Open requisitions' },
    { title: 'Models Loaded', value: pipelineStatus?.models_loaded?.length || 0, icon: <Server size={24} className="text-amber-400" />, trend: 'Active in memory' },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <>
      <AnimatedBackground />
      <div className="flex flex-col space-y-8">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="font-display text-3xl font-semibold tracking-tight text-white">Operational Metrics</h1>
          <p className="mt-2 text-text-secondary">AI Pipeline Status and Infrastructure Health.</p>
        </motion.div>

        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4"
        >
          {statCards.map((stat, idx) => (
            <motion.div key={idx} variants={itemVariants} className="h-full">
              <TiltCard>
                <Card glass className="h-full border-white/10 bg-white/5 transition-all hover:bg-white/10 group">
                  <CardContent className="flex items-center gap-4 p-6">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-black/40 border border-white/10 group-hover:scale-110 transition-transform duration-300">
                      {stat.icon}
                    </div>
                    <div className="flex flex-col">
                      <p className="text-sm font-medium text-text-secondary">{stat.title}</p>
                      {isLoading ? (
                        <Skeleton className="mt-1 h-8 w-20" />
                      ) : (
                        <h3 className="text-2xl font-semibold text-white">{stat.value}</h3>
                      )}
                      <p className="mt-1 text-xs text-text-muted">{stat.trend}</p>
                    </div>
                  </CardContent>
                </Card>
              </TiltCard>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="grid gap-6 md:grid-cols-2"
        >
          <Card glass>
            <CardHeader>
              <CardTitle>Loaded Models</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : (
                <div className="flex flex-col gap-3">
                  {pipelineStatus?.models_loaded?.map((model, idx) => (
                    <motion.div 
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + (idx * 0.1) }}
                      key={model} 
                      className="flex items-center gap-3 rounded-lg border border-white/5 bg-black/20 p-4 transition-colors hover:bg-white/5"
                    >
                      <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse" />
                      <span className="font-mono text-sm text-text-primary">{model}</span>
                    </motion.div>
                  )) || <p className="text-sm text-text-secondary">No models loaded.</p>}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </>
  );
}
