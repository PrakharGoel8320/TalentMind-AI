'use client';
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Send, Bot, ExternalLink, Loader2, TerminalSquare } from 'lucide-react';
import { useRunAgent } from '@/features/agent/queries';
import ReactMarkdown from 'react-markdown';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';

export default function AgentPanel({ jobId }: { jobId: string }) {
  const [prompt, setPrompt] = useState("Find the strongest candidates for this role and propose an action.");
  const [messages, setMessages] = useState<{role: 'user'|'agent', content: string}[]>([]);
  const { mutate: runAgent, isPending } = useRunAgent();
  const router = useRouter();

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const userMessage = prompt;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setPrompt('');

    runAgent({ jobId, request: userMessage }, {
      onSuccess: (data) => {
        let agentContent = data.explanation || "No explanation provided.";
        
        if (data.status === "proposed_action" || agentContent.includes("propose")) {
           agentContent += "\n\n**Action Proposed!** Check the [Approvals Queue](/approvals) to review and execute.";
        }

        if (data.errors && data.errors.length > 0) {
           agentContent += "\n\n**Errors:**\n" + data.errors.map(e => `- ${e}`).join('\n');
        }

        setMessages(prev => [...prev, { role: 'agent', content: agentContent }]);
      },
      onError: (err: any) => {
        setMessages(prev => [...prev, { role: 'agent', content: `Error: ${err.message}` }]);
      }
    });
  };

  return (
    <div className="relative flex h-full flex-col overflow-hidden rounded-xl border border-white/10 bg-surface shadow-2xl">
      {/* Terminal Header */}
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/5 px-4 py-3">
        <TerminalSquare size={16} className="text-text-secondary" />
        <span className="font-mono text-xs uppercase tracking-widest text-text-muted">Secure Agent Terminal</span>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4 min-h-[300px]">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center opacity-70 text-text-secondary">
            <div className="relative mb-6 flex h-16 w-16 items-center justify-center rounded-full border border-blue-500/30 bg-blue-500/10 shadow-[0_0_30px_rgba(59,130,246,0.15)]">
              <Bot size={32} className="text-blue-400" />
              <div className="absolute inset-0 animate-ping rounded-full border border-blue-400/50 opacity-20" />
            </div>
            <p className="max-w-[250px] text-center font-mono text-sm leading-relaxed">
              Agent core initialized.<br/>
              Awaiting directive for Job {jobId.substring(0,6)}...
            </p>
          </div>
        ) : (
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={i} 
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[90%] rounded-2xl p-4 ${msg.role === 'user' ? 'border border-white/10 bg-white/10 text-white' : 'rounded-tl-none border-l-2 border-blue-500 bg-transparent text-text-primary'}`}>
                  {msg.role === 'agent' ? (
                    <div className="prose prose-sm prose-invert max-w-none font-mono text-sm prose-p:leading-relaxed">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      {msg.content.includes("Approvals Queue") && (
                        <Button 
                          variant="secondary" 
                          size="sm" 
                          className="mt-4 flex w-full items-center justify-center gap-2 border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
                          onClick={() => router.push('/approvals')}
                        >
                          Review in Approvals <ExternalLink size={14} />
                        </Button>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm">{msg.content}</p>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
        {isPending && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
            <div className="flex items-center gap-3 rounded-r-2xl border-l-2 border-purple-500 bg-transparent p-4 font-mono text-sm text-text-secondary">
              <Loader2 size={16} className="animate-spin text-purple-400" /> Processing semantic search & reasoning...
            </div>
          </motion.div>
        )}
      </div>

      <div className="border-t border-white/10 bg-surface/50 p-4 backdrop-blur-xl">
        <form onSubmit={handleSend} className="flex gap-3">
          <Input 
            className="flex-1 border-white/10 bg-black/50 font-mono text-sm focus:border-blue-500"
            placeholder="Initialize command sequence..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isPending}
          />
          <Button type="submit" disabled={isPending || !prompt.trim()} className="px-4 shadow-[0_0_15px_rgba(255,255,255,0.1)]">
            <Send size={18} />
          </Button>
        </form>
      </div>
    </div>
  );
}
