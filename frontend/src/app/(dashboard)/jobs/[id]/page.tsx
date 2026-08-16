'use client';
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { useJob, useJobMatches, useRankCandidates } from '@/features/jobs/queries';
import { Match } from '@/features/jobs/api';
import { MapPin, Users, Activity, Bot, ArrowRight, ShieldAlert, Cpu, Database } from 'lucide-react';
import { useRouter } from 'next/navigation';
import AgentPanel from '@/components/AgentPanel';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

const ScoreRing = ({ score, label, color }: { score: number, label: string, color: string }) => {
  const percentage = Math.max(0, Math.min(100, Math.round(score * 100)));
  
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative flex h-12 w-12 items-center justify-center">
        <svg className="h-full w-full -rotate-90" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15.915" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
          <motion.circle 
            cx="18" cy="18" r="15.915" fill="none" 
            stroke={color} 
            strokeWidth="3" 
            strokeDasharray={`${percentage}, 100`}
            initial={{ strokeDasharray: "0, 100" }}
            animate={{ strokeDasharray: `${percentage}, 100` }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>
        <span className="absolute font-mono text-[10px] font-bold text-white">{percentage}</span>
      </div>
      <span className="text-[10px] uppercase tracking-wider text-text-muted">{label}</span>
    </div>
  );
};

export default function JobDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { data: job, isLoading: isJobLoading, isError: isJobError } = useJob(params.id);
  const { data: matches, isLoading: isMatchesLoading } = useJobMatches(params.id);
  const { mutate: rankCandidates, isPending: isRanking } = useRankCandidates();

  if (isJobError) {
    return <div className="mx-auto max-w-6xl p-8 text-error">Failed to load job details.</div>;
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-72px)] max-w-[1600px] flex-col gap-8 overflow-hidden p-6 lg:p-8 xl:flex-row">
      
      {/* Left Column: Job Details & Matches */}
      <div className="scrollbar-hide flex flex-1 flex-col gap-6 overflow-y-auto pr-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {isJobLoading ? <Skeleton className="mb-2 h-10 w-64" /> : <h1 className="font-display text-3xl font-semibold tracking-tight text-white lg:text-4xl">{job?.title}</h1>}
            {isJobLoading ? <Skeleton className="h-5 w-40" /> : <p className="mt-1 font-medium text-text-secondary">{job?.department || 'General'} Department</p>}
          </div>
          <Button 
            size="lg"
            className="border-0 bg-white text-black shadow-[0_0_20px_rgba(255,255,255,0.15)] hover:bg-gray-200"
            leftIcon={!isRanking && <Activity size={18} />}
            onClick={() => rankCandidates(params.id)}
            isLoading={isRanking}
          >
            {isRanking ? 'Initiating Pipeline...' : 'Run Ranking Engine'}
          </Button>
        </div>

        <Card className="border-white/10 bg-surface">
          <CardHeader className="border-b border-white/5 bg-black/20 p-4">
            <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-widest text-text-muted">
              <Cpu size={16} /> Job Parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 pt-6">
            {isJobLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-20 w-full bg-white/5" />
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex gap-6 text-sm text-text-primary">
                  <span className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5"><MapPin size={16} className="text-blue-400" /> {job?.location || 'Remote'}</span>
                  <span className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5"><Users size={16} className="text-purple-400" /> {job?.type || 'Full-time'}</span>
                </div>
                <div className="prose prose-sm prose-invert max-w-none text-text-secondary">
                  <ReactMarkdown>{job?.description || ''}</ReactMarkdown>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="mt-4">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold tracking-wide text-white">
            Deterministic Output <span className="rounded border border-blue-500/20 bg-blue-500/10 px-2 py-0.5 text-xs font-normal text-blue-400">Fusion Engine</span>
          </h2>
          {isMatchesLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-32 w-full rounded-2xl bg-white/5" />
              <Skeleton className="h-32 w-full rounded-2xl bg-white/5" />
            </div>
          ) : !matches || matches.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-white/20 bg-white/5 p-12 text-center text-text-secondary backdrop-blur-sm">
              <Database className="mx-auto mb-4 opacity-50" size={32} />
              No matches generated yet. Run the ranking engine above to begin pipeline.
            </div>
          ) : (
            <div className="space-y-4 pb-12">
              {matches.map((match: Match, index: number) => (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  key={match.id}
                >
                  <Card className="group cursor-pointer overflow-hidden border-white/10 bg-surface transition-all hover:border-blue-500/50 hover:shadow-[0_0_30px_rgba(59,130,246,0.1)]" onClick={() => router.push(`/candidates/${match.candidate_id}`)}>
                    <CardContent className="flex flex-col items-center justify-between gap-6 p-5 sm:flex-row">
                      
                      <div className="w-full flex-1">
                        <div className="mb-3 flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-gradient-to-br from-blue-500/20 to-purple-500/20">
                            <span className="font-mono text-sm text-white">{index + 1}</span>
                          </div>
                          <h4 className="text-lg font-semibold text-white transition-colors group-hover:text-blue-400">Candidate {match.candidate_id.substring(0, 8)}</h4>
                          
                          {match.flags && match.flags.length > 0 && (
                            <div className="ml-4 flex gap-2">
                              {match.flags.map(flag => (
                                <span key={flag} className="flex items-center gap-1 rounded-md border border-red-500/30 bg-red-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-red-400">
                                  <ShieldAlert size={12} /> {flag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <div className="mt-4 flex gap-4 sm:gap-8">
                          <ScoreRing score={match.score_components.cross_encoder_score || 0} label="Semantic" color="#3b82f6" />
                          <ScoreRing score={match.score_components.skill_match_score || 0} label="Skills" color="#8b5cf6" />
                          <ScoreRing score={match.score_components.experience_score || 0} label="Experience" color="#ec4899" />
                          <ScoreRing score={match.score_components.behavior_score || 0} label="Behavioral" color="#10b981" />
                        </div>
                      </div>

                      <div className="flex h-full flex-col items-center justify-center border-t border-white/10 pt-4 text-right sm:items-end sm:border-l sm:border-t-0 sm:pl-6 sm:pt-0">
                        <div className="mb-1 text-xs uppercase tracking-widest text-text-muted">Final Rank</div>
                        <div className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-4xl font-bold text-transparent">{(match.final_score * 100).toFixed(1)}%</div>
                        <Button variant="ghost" size="sm" className="mt-3 h-auto p-0 text-blue-400 hover:bg-transparent group-hover:text-blue-300" rightIcon={<ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />}>
                          Inspect Profile
                        </Button>
                      </div>
                      
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Column: Agent Panel */}
      <div className="h-full w-full flex-shrink-0 xl:w-[450px]">
        <AgentPanel jobId={params.id} />
      </div>

    </div>
  );
}
