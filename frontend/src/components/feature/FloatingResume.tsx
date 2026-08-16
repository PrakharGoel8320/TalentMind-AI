'use client';

import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { FileText, Database, BrainCircuit } from 'lucide-react';

export function FloatingResume() {
  const { scrollYProgress } = useScroll();
  
  // As user scrolls down, the resume splits into layers
  const z1 = useTransform(scrollYProgress, [0, 0.3], [0, 50]);
  const z2 = useTransform(scrollYProgress, [0, 0.3], [0, 100]);
  const z3 = useTransform(scrollYProgress, [0, 0.3], [0, 150]);
  
  const opacityLayer = useTransform(scrollYProgress, [0, 0.1], [0, 1]);
  const rotateX = useTransform(scrollYProgress, [0, 0.3], [0, 60]);
  const rotateZ = useTransform(scrollYProgress, [0, 0.3], [0, -20]);

  return (
    <div className="relative w-full h-[600px] flex items-center justify-center select-none" style={{ perspective: '1200px' }}>
      <motion.div 
        className="relative w-80 h-[400px]"
        style={{
          rotateX,
          rotateZ,
          transformStyle: "preserve-3d"
        }}
      >
        {/* Layer 3: ML Inference (Bottom) */}
        <motion.div 
          className="absolute inset-0 flex flex-col items-center justify-center gap-4 rounded-xl border border-purple-500/30 bg-purple-900/10 backdrop-blur-md shadow-2xl"
          style={{ translateZ: z3, opacity: opacityLayer }}
        >
          <BrainCircuit size={48} className="text-purple-400" />
          <div className="text-sm font-semibold text-purple-300">Cross-Encoder Reasoning</div>
          <div className="w-3/4 h-2 bg-purple-500/20 rounded overflow-hidden">
            <motion.div 
              className="h-full bg-purple-500" 
              initial={{ width: 0 }}
              animate={{ width: '85%' }}
              transition={{ duration: 2, repeat: Infinity, repeatType: 'reverse' }}
            />
          </div>
        </motion.div>

        {/* Layer 2: FAISS Retrieval (Middle) */}
        <motion.div 
          className="absolute inset-0 flex flex-col items-center justify-center gap-4 rounded-xl border border-blue-500/30 bg-blue-900/10 backdrop-blur-md shadow-2xl"
          style={{ translateZ: z2, opacity: opacityLayer }}
        >
          <Database size={48} className="text-blue-400" />
          <div className="text-sm font-semibold text-blue-300">FAISS Semantic Search</div>
          <div className="flex gap-2">
            {[1, 2, 3].map(i => (
              <motion.div 
                key={i}
                className="w-8 h-8 rounded border border-blue-400/30 bg-blue-500/20"
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, delay: i * 0.2, repeat: Infinity }}
              />
            ))}
          </div>
        </motion.div>

        {/* Layer 1: PyMuPDF Extraction (Top/Base) */}
        <motion.div 
          className="absolute inset-0 flex flex-col p-6 gap-4 rounded-xl border border-white/20 bg-[#0a0a0a]/80 backdrop-blur-md shadow-2xl"
          style={{ translateZ: z1 }}
        >
          <div className="flex items-center gap-3 border-b border-white/10 pb-4">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center">
              <FileText size={24} className="text-white/80" />
            </div>
            <div>
              <div className="w-32 h-4 bg-white/20 rounded mb-2" />
              <div className="w-20 h-3 bg-white/10 rounded" />
            </div>
          </div>
          
          <div className="flex-1 flex flex-col gap-3 mt-2">
            <div className="w-full h-3 bg-white/10 rounded" />
            <div className="w-5/6 h-3 bg-white/10 rounded" />
            <div className="w-4/6 h-3 bg-white/10 rounded" />
            <div className="w-full h-3 bg-white/10 rounded mt-4" />
            <div className="w-3/4 h-3 bg-white/10 rounded" />
          </div>
        </motion.div>
        
      </motion.div>
    </div>
  );
}
