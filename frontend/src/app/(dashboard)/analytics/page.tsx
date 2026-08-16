'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp } from 'lucide-react';

const MOCK_CHART_DATA_PIPELINE = [
  { stage: 'Sourced', count: 1240 },
  { stage: 'Applied', count: 850 },
  { stage: 'Screened', count: 420 },
  { stage: 'Interviewed', count: 180 },
  { stage: 'Offered', count: 45 },
  { stage: 'Hired', count: 32 },
];

const MOCK_CHART_DATA_TRENDS = [
  { month: 'Jan', hires: 4, timeToHire: 45 },
  { month: 'Feb', hires: 6, timeToHire: 42 },
  { month: 'Mar', hires: 5, timeToHire: 38 },
  { month: 'Apr', hires: 8, timeToHire: 35 },
  { month: 'May', hires: 12, timeToHire: 30 },
  { month: 'Jun', hires: 15, timeToHire: 28 },
];

export default function AnalyticsPage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="mx-auto flex max-w-7xl flex-col space-y-8">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white">Analytics & Reporting</h1>
        <p className="mt-2 text-text-secondary">Deep dive into your recruitment metrics.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="h-full">
          <Card className="flex h-full flex-col border-white/10 bg-surface">
            <CardHeader className="border-b border-white/10 bg-white/5">
              <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-widest text-text-muted">
                <BarChart3 size={16} /> Recruitment Funnel Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col p-6 min-h-[400px]">
              {isLoading ? (
                <Skeleton className="h-full w-full bg-white/5" />
              ) : (
                <div className="h-full w-full min-h-[300px] flex-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={MOCK_CHART_DATA_PIPELINE} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={true} vertical={false} />
                      <XAxis type="number" stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis dataKey="stage" type="category" stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} width={100} />
                      <Tooltip 
                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                        contentStyle={{ backgroundColor: '#0a0a0a', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                        itemStyle={{ color: '#3b82f6' }}
                      />
                      <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={32} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="h-full">
          <Card className="flex h-full flex-col border-white/10 bg-surface">
            <CardHeader className="border-b border-white/10 bg-white/5">
              <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-widest text-text-muted">
                <TrendingUp size={16} /> Time to Hire Trend (Days)
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col p-6 min-h-[400px]">
              {isLoading ? (
                <Skeleton className="h-full w-full bg-white/5" />
              ) : (
                <div className="h-full w-full min-h-[300px] flex-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={MOCK_CHART_DATA_TRENDS} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                      <defs>
                        <linearGradient id="colorHires" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                      <XAxis dataKey="month" stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0a0a0a', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                        itemStyle={{ color: '#10b981' }}
                      />
                      <Area type="monotone" dataKey="hires" stroke="#10b981" fillOpacity={1} fill="url(#colorHires)" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
