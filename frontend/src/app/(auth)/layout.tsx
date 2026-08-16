import React from 'react';
import Link from 'next/link';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen w-full bg-background text-text-primary">
      <div className="hidden w-1/2 flex-col justify-between border-r border-white/10 bg-surface/50 p-12 lg:flex">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-accent-blue shadow-[0_0_20px_rgba(59,130,246,0.5)]" />
          <Link href="/" className="font-display text-2xl font-bold tracking-tight text-white">
            TalentMind AI
          </Link>
        </div>
        <div>
          <h1 className="font-display text-4xl font-semibold leading-tight text-white">
            The next-generation <br />
            <span className="text-gradient-accent">recruitment intelligence</span> platform.
          </h1>
          <p className="mt-4 text-lg text-text-secondary">
            Deterministic candidate ranking. Agentic reasoning. Human-in-the-loop security.
          </p>
        </div>
        <div className="text-sm text-text-muted">
          &copy; {new Date().getFullYear()} TalentMind AI.
        </div>
      </div>
      <div className="flex w-full items-center justify-center p-8 lg:w-1/2">
        <div className="w-full max-w-md">
          {children}
        </div>
      </div>
    </div>
  );
}
