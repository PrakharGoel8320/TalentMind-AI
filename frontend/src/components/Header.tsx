'use client';
import React from 'react';
import { Bell, Search, Moon, Sun } from 'lucide-react';
import { useThemeStore } from '@/store/themeStore';
import { Input } from './ui/Input';

export function Header() {
  const { isDark, toggleTheme } = useThemeStore();

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-white/10 bg-background/80 px-6 backdrop-blur-md">
      <div className="flex w-full max-w-md items-center">
        <div className="w-full">
          <Input 
            placeholder="Search candidates, jobs..." 
            leftIcon={<Search size={18} />} 
            className="h-9 bg-white/5 border-transparent focus-visible:bg-white/10"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button 
          onClick={toggleTheme} 
          className="flex h-9 w-9 items-center justify-center rounded-full text-text-secondary hover:bg-white/10 hover:text-white transition-colors"
          aria-label="Toggle Theme"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button className="relative flex h-9 w-9 items-center justify-center rounded-full text-text-secondary hover:bg-white/10 hover:text-white transition-colors">
          <Bell size={18} />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-accent-blue ring-2 ring-background" />
        </button>
        
        <div className="flex items-center gap-3 pl-4 border-l border-white/10">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin" alt="Admin" className="h-8 w-8 rounded-full bg-white/10" />
          <div className="hidden flex-col md:flex">
            <span className="text-sm font-medium text-text-primary leading-none">Jane Doe</span>
            <span className="text-xs text-text-secondary mt-1">Recruiter</span>
          </div>
        </div>
      </div>
    </header>
  );
}
