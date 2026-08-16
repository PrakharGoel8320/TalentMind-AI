'use client';

import React from 'react';
import { motion } from 'framer-motion';

export function RankingPipeline() {
  return (
    <div className="w-full max-w-4xl mx-auto h-[400px] flex items-center justify-between relative select-none">
      
      {/* Input */}
      <motion.div 
        className="w-48 h-64 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md flex flex-col items-center justify-center p-6 relative z-10 shadow-xl"
        initial={{ opacity: 0, x: -50 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, margin: "-100px" }}
      >
        <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-4">
          <span className="text-2xl">📄</span>
        </div>
        <h3 className="font-semibold text-center mb-2">Raw Data</h3>
        <p className="text-xs text-center text-white/50">PyMuPDF Parsed Text & Metadata</p>
      </motion.div>

      {/* Connecting Flow */}
      <div className="absolute left-48 right-48 top-1/2 -translate-y-1/2 h-1 bg-white/5 z-0">
        <motion.div 
          className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
          initial={{ scaleX: 0, transformOrigin: 'left' }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1.5, delay: 0.2 }}
        />
        
        {/* Particles traveling */}
        {[1, 2, 3].map(i => (
          <motion.div
            key={i}
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)]"
            initial={{ left: 0, opacity: 0 }}
            animate={{ left: '100%', opacity: [0, 1, 0] }}
            transition={{ duration: 2, repeat: Infinity, delay: i * 0.6 }}
          />
        ))}
      </div>

      {/* Middle: Engine */}
      <motion.div 
        className="w-64 h-80 rounded-xl border border-white/20 flex flex-col items-center justify-center p-6 relative z-10 bg-black/40 backdrop-blur-3xl shadow-[0_0_50px_rgba(139,92,246,0.15)]"
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ delay: 0.4 }}
      >
        <div className="w-full flex gap-2 mb-6">
          <div className="flex-1 h-2 bg-blue-500/20 rounded overflow-hidden">
             <motion.div className="h-full bg-blue-500" initial={{ width: 0 }} whileInView={{ width: '80%' }} transition={{ delay: 1 }} />
          </div>
          <div className="flex-1 h-2 bg-purple-500/20 rounded overflow-hidden">
             <motion.div className="h-full bg-purple-500" initial={{ width: 0 }} whileInView={{ width: '60%' }} transition={{ delay: 1.2 }} />
          </div>
          <div className="flex-1 h-2 bg-pink-500/20 rounded overflow-hidden">
             <motion.div className="h-full bg-pink-500" initial={{ width: 0 }} whileInView={{ width: '90%' }} transition={{ delay: 1.4 }} />
          </div>
        </div>
        
        <h3 className="font-semibold text-center mb-2 text-lg">Fusion Engine</h3>
        <p className="text-sm text-center text-white/50 mb-6">Deterministic Multi-Factor Scoring</p>
        
        <div className="w-24 h-24 rounded-full border-4 border-white/10 flex items-center justify-center relative">
           <motion.svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
             <motion.circle 
               cx="50" cy="50" r="46" 
               fill="none" 
               stroke="url(#gradient)" 
               strokeWidth="4"
               strokeLinecap="round"
               initial={{ strokeDasharray: "0 300" }}
               whileInView={{ strokeDasharray: "220 300" }}
               transition={{ duration: 1.5, delay: 0.8 }}
             />
             <defs>
               <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                 <stop offset="0%" stopColor="#3b82f6" />
                 <stop offset="100%" stopColor="#ec4899" />
               </linearGradient>
             </defs>
           </motion.svg>
           <span className="text-2xl font-bold">89</span>
        </div>
      </motion.div>

      {/* Output */}
      <motion.div 
        className="w-48 h-64 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md flex flex-col items-center justify-center p-6 relative z-10 shadow-xl"
        initial={{ opacity: 0, x: 50 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ delay: 0.6 }}
      >
        <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-4 text-green-400">
          <span className="text-2xl">✓</span>
        </div>
        <h3 className="font-semibold text-center mb-2">Ranked Talent</h3>
        <p className="text-xs text-center text-white/50">Ready for Agentic Review</p>
      </motion.div>
      
    </div>
  );
}
