import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-background text-text-primary selection:bg-accent-blue/30 selection:text-white">
      <header className="fixed top-0 z-50 w-full border-b border-white/5 bg-background/50 backdrop-blur-xl transition-all">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-accent-blue shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
            <span className="font-display text-lg font-semibold tracking-tight text-white">TalentMind AI</span>
          </Link>
          <nav className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="hidden sm:inline-flex">Log in</Button>
            </Link>
            <Link href="/register">
              <Button variant="primary" size="sm">Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1">
        {children}
      </main>
      <footer className="border-t border-white/5 py-12">
        <div className="mx-auto max-w-7xl px-6 text-center text-sm text-text-secondary">
          <p>&copy; {new Date().getFullYear()} TalentMind AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
