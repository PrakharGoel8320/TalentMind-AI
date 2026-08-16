'use client';
import React from 'react';
import { motion } from 'framer-motion';

export function AnimatedBackground() {
  return (
    <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none bg-black">
      {/* Dynamic Mesh Layer */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.4) 0%, transparent 50%)
          `,
          filter: 'blur(60px)'
        }}
      />
      
      {/* Floating Orbs */}
      <motion.div
        animate={{
          x: [0, 100, 0],
          y: [0, 50, 0],
          scale: [1, 1.2, 1]
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute top-[10%] left-[20%] w-[30vw] h-[30vw] rounded-full mix-blend-screen"
        style={{
          background: 'radial-gradient(circle, rgba(59,130,246,0.3) 0%, rgba(0,0,0,0) 70%)',
          filter: 'blur(40px)'
        }}
      />
      
      <motion.div
        animate={{
          x: [0, -100, 0],
          y: [0, -50, 0],
          scale: [1, 1.3, 1]
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute bottom-[10%] right-[10%] w-[40vw] h-[40vw] rounded-full mix-blend-screen"
        style={{
          background: 'radial-gradient(circle, rgba(168,85,247,0.2) 0%, rgba(0,0,0,0) 70%)',
          filter: 'blur(50px)'
        }}
      />
    </div>
  );
}
