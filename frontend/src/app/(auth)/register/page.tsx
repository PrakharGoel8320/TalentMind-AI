'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Mail, Lock, User, Briefcase } from 'lucide-react';
import { authApi } from '@/features/auth/api';
import { getApiBaseUrl } from '@/lib/apiClient';
import { useAuth } from '@/providers/AuthProvider';

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    email: '',
    password: ''
  });

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const data = await authApi.register({
        email: formData.email,
        password: formData.password,
        name: formData.name
      });
      // Optionally login directly or push to login
      login(data.access_token, data.user);
      router.push('/dashboard');
    } catch (err: any) {
      if (err?.response) {
        // The server responded with an error status (4xx/5xx).
        const detail = err.response.data?.detail;
        setError(typeof detail === 'string' ? detail : 'Registration failed. Please try again.');
      } else {
        // No response object means the request never reached the backend
        // (wrong API URL, CORS block, mixed content, or server down).
        console.error(`[auth] Register request failed. API base URL = ${getApiBaseUrl()}`, err);
        setError(
          `Cannot reach the server at ${getApiBaseUrl()}. ` +
            'Check that NEXT_PUBLIC_API_URL points to your backend and that the backend is running.'
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="flex flex-col space-y-8">
      <div className="text-center md:text-left">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white">Create an account</h1>
        <p className="mt-2 text-sm text-text-secondary">Start hiring smarter today.</p>
      </div>

      <form className="flex flex-col space-y-4" onSubmit={handleRegister}>
        {error && <div className="rounded-md bg-error/10 p-3 text-sm text-error border border-error/20">{error}</div>}
        <Input 
          label="Full Name" 
          name="name"
          type="text" 
          placeholder="Jane Doe" 
          required 
          value={formData.name}
          onChange={handleChange}
          leftIcon={<User size={16} />}
        />
        <Input 
          label="Company Name" 
          name="company"
          type="text" 
          placeholder="Acme Corp" 
          required 
          value={formData.company}
          onChange={handleChange}
          leftIcon={<Briefcase size={16} />}
        />
        <Input 
          label="Work Email" 
          name="email"
          type="email" 
          placeholder="jane@company.com" 
          required 
          value={formData.email}
          onChange={handleChange}
          leftIcon={<Mail size={16} />}
        />
        <Input 
          label="Password" 
          name="password"
          type="password" 
          placeholder="••••••••" 
          required 
          value={formData.password}
          onChange={handleChange}
          leftIcon={<Lock size={16} />}
        />
        
        <Button type="submit" size="lg" className="mt-4 w-full" isLoading={isLoading}>
          Create account
        </Button>
      </form>

      <div className="text-center text-sm text-text-secondary">
        <p>Already have an account? <Link href="/login" className="font-medium text-accent-blue hover:text-blue-400 hover:underline">Sign in</Link></p>
      </div>
    </div>
  );
}
