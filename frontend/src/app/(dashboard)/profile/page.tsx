'use client';
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { User, Mail, Briefcase, Phone, Camera } from 'lucide-react';

export default function ProfilePage() {
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 800);
  };

  return (
    <div className="mx-auto flex max-w-4xl flex-col space-y-8">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white">My Profile</h1>
        <p className="mt-2 text-text-secondary">Update your personal information.</p>
      </div>

      <Card className="border-white/10 bg-surface">
        <CardHeader className="border-b border-white/10 bg-white/5">
          <CardTitle>Profile Details</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="mb-8 flex flex-col items-center gap-6 sm:flex-row">
            <div className="relative">
              <div className="h-24 w-24 overflow-hidden rounded-full border-2 border-white/10 bg-white/5">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin" alt="Profile" className="h-full w-full object-cover" />
              </div>
              <button className="absolute bottom-0 right-0 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-surface shadow-lg transition-transform hover:scale-110">
                <Camera size={14} className="text-text-secondary" />
              </button>
            </div>
            <div className="flex flex-col items-center gap-3 sm:items-start">
              <Button variant="secondary" size="sm">Change Avatar</Button>
              <Button variant="ghost" size="sm" className="text-error hover:bg-error/10 hover:text-red-400">Remove</Button>
            </div>
          </div>
          
          <form onSubmit={handleSave} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input 
                label="Full Name" 
                defaultValue="Jane Doe"
                leftIcon={<User size={16} />}
              />
              <Input 
                label="Role" 
                defaultValue="Senior Technical Recruiter"
                leftIcon={<Briefcase size={16} />}
              />
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input 
                label="Email Address" 
                type="email"
                defaultValue="jane@talentmind.ai"
                leftIcon={<Mail size={16} />}
              />
              <Input 
                label="Phone Number" 
                type="tel"
                defaultValue="+1 (555) 123-4567"
                leftIcon={<Phone size={16} />}
              />
            </div>
            
            <div className="flex justify-end pt-4">
              <Button type="submit" isLoading={isSaving} className="w-full sm:w-auto">Save Changes</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
