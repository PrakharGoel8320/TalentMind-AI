'use client';
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useThemeStore } from '@/store/themeStore';
import { Moon, Sun, Monitor, Bell, Shield, Key } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SettingsPage() {
  const { isDark, toggleTheme } = useThemeStore();
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('appearance');

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 800);
  };

  const navItems = [
    { id: 'appearance', label: 'Appearance', icon: Monitor },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'api', label: 'API Keys', icon: Key },
  ];

  return (
    <div className="mx-auto flex max-w-5xl flex-col space-y-8">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white">Settings</h1>
        <p className="mt-2 text-text-secondary">Manage your account settings and preferences.</p>
      </div>

      <div className="flex flex-col gap-8 md:flex-row">
        <div className="w-full md:w-64">
          <nav className="flex flex-col space-y-1">
            {navItems.map(item => (
              <button 
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === item.id 
                    ? 'bg-accent-blue/10 text-accent-blue' 
                    : 'text-text-secondary hover:bg-white/5 hover:text-white'
                }`}
              >
                <item.icon size={18} /> {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex-1">
          {activeTab === 'appearance' && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="border-white/10 bg-surface">
                <CardHeader className="border-b border-white/10 bg-white/5">
                  <CardTitle>Appearance</CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <h3 className="font-medium text-white">Theme Preference</h3>
                      <p className="mt-1 text-sm text-text-secondary">Choose between light and dark mode.</p>
                    </div>
                    <div className="flex items-center gap-4 rounded-xl border border-white/10 p-1">
                      <button 
                        className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-colors ${
                          !isDark ? 'bg-white/10 text-white' : 'text-text-secondary hover:text-white'
                        }`}
                        onClick={() => isDark && toggleTheme()}
                      >
                        <Sun size={18} />
                        <span className="text-sm font-medium">Light</span>
                      </button>
                      <button 
                        className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-colors ${
                          isDark ? 'bg-white/10 text-white' : 'text-text-secondary hover:text-white'
                        }`}
                        onClick={() => !isDark && toggleTheme()}
                      >
                        <Moon size={18} />
                        <span className="text-sm font-medium">Dark</span>
                      </button>
                    </div>
                  </div>

                  <div className="my-8 h-px w-full bg-white/10" />

                  <div className="flex justify-end">
                    <Button isLoading={isSaving} onClick={handleSave}>Save Changes</Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {activeTab !== 'appearance' && (
            <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-white/10 bg-white/5 text-text-secondary">
              <p>This settings pane is not yet implemented.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
