'use client';
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { User, Mail, Briefcase, FileText } from 'lucide-react';
import { useCandidate } from '@/features/candidates/queries';
import { notFound } from 'next/navigation';
import { motion } from 'framer-motion';

export default function CandidateProfilePage({ params }: { params: { id: string } }) {
  const { data: candidate, isLoading, isError } = useCandidate(params.id);

  if (isError) {
    return (
      <div className="mx-auto max-w-4xl space-y-6 p-8 text-center text-error">
        Failed to load candidate profile.
      </div>
    );
  }

  if (!isLoading && !candidate) {
    return notFound();
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col space-y-6">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white">Candidate Profile</h1>
        <p className="mt-2 text-text-secondary">Structured data parsed from resume.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="h-full border-white/10 bg-surface">
            <CardHeader className="border-b border-white/10 bg-white/5">
              <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-widest text-text-muted">
                <User size={16} /> Personal Info
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
               {isLoading || !candidate ? <Skeleton className="h-20 w-full bg-white/5" /> : (
                 <div className="flex flex-col gap-4">
                   <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-blue/10 text-xl font-bold text-accent-blue">
                        {candidate.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium text-white">{candidate.name}</p>
                        <p className="flex items-center gap-2 text-sm text-text-secondary"><Mail size={14} className="text-text-muted" /> {candidate.email}</p>
                      </div>
                   </div>
                   
                   <div className="mt-2 space-y-3 rounded-lg border border-white/5 bg-black/20 p-4 text-sm text-text-secondary">
                     <div className="flex items-center justify-between">
                       <span className="text-text-muted">Expected Role</span>
                       <span className="font-medium text-white">{candidate.profile_jsonb?.role || candidate.role || "Unspecified"}</span>
                     </div>
                     <div className="flex items-center justify-between">
                       <span className="text-text-muted">Experience</span>
                       <span className="font-medium text-white">{candidate.profile_jsonb?.experience_years ?? candidate.experience ?? "0"} years</span>
                     </div>
                   </div>
                 </div>
               )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="h-full border-white/10 bg-surface">
            <CardHeader className="border-b border-white/10 bg-white/5">
              <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-widest text-text-muted">
                <Briefcase size={16} /> Parsed Skills
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
               {isLoading || !candidate ? <Skeleton className="h-20 w-full bg-white/5" /> : (
                 <div className="flex flex-wrap gap-2">
                   {((candidate.profile_jsonb?.skills?.length ?? 0) > 0 || (candidate.skills?.length ?? 0) > 0) ? (
                     (candidate.profile_jsonb?.skills || candidate.skills).map((skill: string, idx: number) => (
                       <motion.span 
                         initial={{ opacity: 0, scale: 0.9 }}
                         animate={{ opacity: 1, scale: 1 }}
                         transition={{ delay: 0.3 + (idx * 0.05) }}
                         key={skill} 
                         className="rounded-full border border-purple-500/20 bg-purple-500/10 px-3 py-1 text-xs font-medium text-purple-300"
                       >
                         {skill}
                       </motion.span>
                     ))
                   ) : (
                     <span className="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-white/10 p-6 text-sm text-text-muted">
                       <FileText size={16} /> No skills parsed yet.
                     </span>
                   )}
                 </div>
               )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
