'use client';
import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { ArrowRight, ChevronRight, Lock, Brain, Zap, ShieldCheck, Database } from 'lucide-react';
import Link from 'next/link';
import { TiltCard } from '@/components/ui/TiltCard';
import { FloatingResume } from '@/components/feature/FloatingResume';
import { RankingPipeline } from '@/components/feature/RankingPipeline';

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);
  const heroY = useTransform(scrollYProgress, [0, 0.2], [0, 50]);

  return (
    <div className="w-full bg-black text-white min-h-screen selection:bg-blue-500/30">
      
      {/* Dynamic Background Noise & Gradients */}
      <div className="fixed inset-0 pointer-events-none z-0 opacity-40">
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-20 mix-blend-overlay"></div>
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-blue-900/20 blur-[120px]"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-purple-900/20 blur-[120px]"></div>
      </div>

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center pt-20 px-6 overflow-hidden z-10">
        <motion.div 
          style={{ opacity: heroOpacity, scale: heroScale, y: heroY }}
          className="flex flex-col items-center max-w-5xl mx-auto text-center"
        >
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md mb-8 text-sm font-medium tracking-wide"
          >
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            TalentMind AI is live
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
            className="font-display text-6xl md:text-8xl font-semibold tracking-tighter mb-6 leading-tight text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60"
          >
            Recruitment Intelligence,<br/>
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">Engineered with Evidence.</span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="text-xl md:text-2xl text-white/50 max-w-2xl mb-12 font-light leading-relaxed"
          >
            Transform your engineering hiring process with deterministic multi-factor scoring, semantic FAISS retrieval, and autonomous LangGraph agents.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Link href="/register">
              <Button size="lg" className="w-full sm:w-auto h-14 px-8 text-lg bg-white text-black hover:bg-gray-200 border-0 group">
                Start Trial 
                <ArrowRight size={20} className="ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto h-14 px-8 text-lg bg-white/5 hover:bg-white/10 group backdrop-blur-md">
                Enter Dashboard
                <ChevronRight size={20} className="ml-2 group-hover:translate-x-1 transition-transform text-white/50" />
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Feature 1: The Pipeline */}
      <section className="relative min-h-screen flex flex-col items-center justify-center py-32 px-6 z-10 border-t border-white/5 bg-gradient-to-b from-transparent to-black/50">
        <div className="max-w-6xl w-full mx-auto flex flex-col lg:flex-row items-center gap-16">
          <div className="flex-1 space-y-6">
            <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight text-white/90">
              Deterministic precision. <br/>Zero hallucinations.
            </h2>
            <p className="text-lg text-white/50 leading-relaxed">
              We process resumes through PyMuPDF, extract semantic meaning using sentence-transformers, and rank them deterministically via a Fusion Engine. We don't guess—we calculate.
            </p>
            <ul className="space-y-4 pt-4">
              {[
                { icon: <Brain size={20}/>, text: 'Cross-Encoder Reranking (ms-marco)' },
                { icon: <Database size={20}/>, text: 'FAISS Vector Search' },
                { icon: <Zap size={20}/>, text: 'Deterministic Rule Engine' }
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-4 text-white/70">
                  <div className="w-10 h-10 rounded-full bg-white/5 backdrop-blur-md border border-white/10 flex items-center justify-center text-blue-400">
                    {item.icon}
                  </div>
                  {item.text}
                </li>
              ))}
            </ul>
          </div>
          <div className="flex-1 w-full h-[500px]">
             <FloatingResume />
          </div>
        </div>
      </section>

      {/* Feature 2: Ranking Engine */}
      <section className="relative min-h-screen flex flex-col items-center justify-center py-32 px-6 z-10 border-t border-white/5">
        <div className="max-w-6xl w-full mx-auto flex flex-col-reverse lg:flex-row items-center gap-16">
          <div className="flex-1 w-full">
             <RankingPipeline />
          </div>
          <div className="flex-1 space-y-6">
            <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight text-white/90">
              Multi-factor scoring.
            </h2>
            <p className="text-lg text-white/50 leading-relaxed">
              Every candidate is evaluated on semantic relevance, exact skill match, years of experience, and behavioral flags. The Fusion engine normalizes these scores into a unified, transparent rank.
            </p>
            <div className="pt-6">
              <Link href="/dashboard">
                <Button variant="ghost" className="text-blue-400 hover:text-blue-300 px-0 group">
                  Explore the dashboard <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
      
      {/* Feature 3: Agentic Intelligence */}
      <section className="relative min-h-screen flex flex-col items-center justify-center py-32 px-6 z-10 border-t border-white/5 bg-gradient-to-b from-transparent to-blue-900/10">
        <div className="max-w-6xl w-full mx-auto flex flex-col lg:flex-row items-center gap-16">
          <div className="flex-1 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <Brain size={14} /> Agentic Reasoning
            </div>
            <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight text-white/90">
              AI that reads between the lines.
            </h2>
            <p className="text-lg text-white/50 leading-relaxed">
              Powered by LangGraph, our intelligent agent analyzes candidate evidence, explains scoring anomalies, and proactively proposes next steps based on deep contextual understanding.
            </p>
          </div>
          <div className="flex-1 w-full flex items-center justify-center">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.7 }}
              className="relative w-full max-w-md aspect-square rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 flex flex-col p-6 overflow-hidden shadow-2xl"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 z-0" />
              <div className="relative z-10 flex flex-col h-full space-y-4">
                <div className="flex items-center gap-3 border-b border-white/10 pb-4">
                  <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                    <Brain size={16} className="text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-white/90">Agent Analysis</h3>
                    <p className="text-xs text-white/50">Evaluating candidate fit...</p>
                  </div>
                </div>
                <div className="flex-1 space-y-3 pt-2">
                  <motion.div initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="p-3 rounded-lg bg-white/5 border border-white/5 text-sm text-white/70 shadow-sm">
                    "This candidate has a 92% semantic match for the Senior React Developer role, but lacks direct experience with GraphQL mentioned in the requirements."
                  </motion.div>
                  <motion.div initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.8 }} className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-sm text-blue-200 shadow-sm">
                    Proposing action: <span className="font-mono text-xs bg-black/30 px-1 rounded">EMAIL_CANDIDATE</span> to clarify GraphQL experience.
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Feature 4: Human in the Loop & Security */}
      <section className="relative min-h-screen flex flex-col items-center justify-center py-32 px-6 z-10 border-t border-white/5 overflow-hidden">
        <div className="max-w-6xl w-full mx-auto text-center mb-16">
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight text-white/90 mb-4">
            AI Proposes. <br/><span className="text-blue-400">Humans Decide.</span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            We maintain strict boundaries. Agents can reason and propose actions, but they can never execute external operations without explicit human authorization.
          </p>
        </div>

        <div className="max-w-4xl w-full mx-auto relative h-[400px] flex items-center justify-center">
          {/* Visual Barrier */}
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              whileInView={{ height: '100%', opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1, delay: 0.5 }}
              className="w-px bg-gradient-to-b from-transparent via-blue-500 to-transparent relative shadow-[0_0_15px_rgba(59,130,246,0.8)]"
            >
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-black px-4 py-2 border border-blue-500/50 rounded-full text-xs font-mono text-blue-400 whitespace-nowrap flex items-center gap-2">
                <ShieldCheck size={14} /> assert_action_approved()
              </div>
            </motion.div>
          </div>

          <div className="w-full flex justify-between items-center px-4 md:px-12 relative z-0">
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="flex flex-col items-center gap-4"
            >
              <div className="w-24 h-24 rounded-full border border-white/10 bg-white/5 backdrop-blur-md flex items-center justify-center">
                <Brain size={32} className="text-white/40" />
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-white/90">Agent</div>
                <div className="text-xs text-amber-400/80 mt-1 font-mono bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">PENDING_APPROVAL</div>
              </div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="w-24 h-24 rounded-full border border-blue-500/30 bg-blue-500/5 flex items-center justify-center">
                <Lock size={32} className="text-blue-400" />
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-white/90">Execution</div>
                <div className="text-xs text-green-400/80 mt-1 font-mono bg-green-400/10 px-2 py-0.5 rounded border border-green-400/20">AUTHORIZED</div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="relative py-32 px-6 z-10 border-t border-white/5 flex flex-col items-center justify-center text-center">
        <h2 className="font-display text-4xl md:text-6xl font-semibold tracking-tight mb-8">Ready to upgrade?</h2>
        <Link href="/register">
          <Button size="lg" className="h-14 px-8 text-lg bg-white text-black hover:bg-gray-200 border-0">
            Get Started Now
          </Button>
        </Link>
      </section>
    </div>
  );
}
