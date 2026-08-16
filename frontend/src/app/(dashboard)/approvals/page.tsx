"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/apiClient";
import { ShieldAlert, CheckCircle2, Clock, Play } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { motion } from "framer-motion";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeAction, setActiveAction] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setError(null);
    try {
      const res = await apiClient.get("/approvals/");
      setApprovals(res.data || []);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to load approvals.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleAction = async (id: string, action: "approve" | "reject" | "execute") => {
    setActiveAction(`${id}:${action}`);
    setError(null);
    try {
      await apiClient.post(`/approvals/${id}/${action}`);
      await fetchApprovals();
    } catch (e: any) {
      setError(e?.response?.data?.detail || `Failed to ${action} action.`);
    } finally {
      setActiveAction(null);
    }
  };

  if (loading) return <div className="p-8 text-text-secondary">Loading approvals...</div>;

  return (
    <div className="flex flex-col space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white flex items-center gap-3">
          <ShieldAlert className="text-warning" size={28} />
          Human-In-The-Loop Approvals
        </h1>
        <p className="mt-2 text-text-secondary">Review and authorize actions proposed by the AI Agent.</p>
      </div>

      {error && (
        <div className="rounded-lg border border-error/20 bg-error/10 p-4 text-sm text-error">
          {error}
        </div>
      )}

      {approvals.length === 0 ? (
        <Card className="border-white/10 bg-white/5 border-dashed">
          <CardContent className="flex flex-col items-center justify-center p-12 text-center text-text-muted">
            <CheckCircle2 size={48} className="mb-4 opacity-20" />
            <p className="text-lg font-medium text-text-secondary">All caught up</p>
            <p className="text-sm">No pending actions in the queue.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {approvals.map((proposal, idx) => (
            <motion.div
              key={proposal.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <Card className="border-warning/20 bg-surface shadow-[0_0_15px_rgba(245,158,11,0.05)] overflow-hidden">
                <div className="h-1 w-full bg-gradient-to-r from-warning to-error" />
                <CardContent className="flex flex-col p-6 md:flex-row md:items-start md:justify-between gap-6">
                  <div className="flex-1 space-y-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm font-bold tracking-widest text-warning uppercase">{proposal.action_type}</span>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                        proposal.status === 'PENDING_APPROVAL' ? 'bg-warning/10 text-warning border border-warning/20' : 
                        proposal.status === 'APPROVED' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                        proposal.status === 'EXECUTED' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                        'bg-error/10 text-error border border-error/20'
                      }`}>
                        {proposal.status === 'PENDING_APPROVAL' && <Clock size={12} />}
                        {proposal.status === 'APPROVED' && <CheckCircle2 size={12} />}
                        {proposal.status === 'EXECUTED' && <Play size={12} />}
                        {proposal.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-text-muted uppercase text-[10px] font-bold tracking-wider block mb-1">Target ID</span>
                        <span className="font-mono text-text-secondary">{proposal.target_id.substring(0,8)}</span>
                      </div>
                      {proposal.created_at && (
                        <div>
                          <span className="text-text-muted uppercase text-[10px] font-bold tracking-wider block mb-1">Timestamp</span>
                          <span className="text-text-secondary">{new Date(proposal.created_at).toLocaleString()}</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <span className="text-text-muted uppercase text-[10px] font-bold tracking-wider block mb-1">Agent Reason</span>
                      <p className="text-sm text-text-primary bg-white/5 p-3 rounded-md border border-white/5">{proposal.reason}</p>
                    </div>
                    
                    {proposal.payload && (
                      <div className="rounded-lg border border-white/10 bg-black/40 p-4 text-sm font-mono">
                        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-white/10">
                          <span className="text-text-muted">Payload Details</span>
                        </div>
                        {proposal.payload.recipient && <p className="mb-2"><span className="text-text-muted">To:</span> <span className="text-blue-400">{proposal.payload.recipient}</span></p>}
                        {proposal.payload.subject && <p className="mb-2"><span className="text-text-muted">Subject:</span> <span className="text-text-primary">{proposal.payload.subject}</span></p>}
                        {proposal.payload.body && (
                          <div className="mt-4">
                            <span className="text-text-muted block mb-2">Body:</span>
                            <pre className="whitespace-pre-wrap text-text-secondary font-sans text-sm bg-white/5 p-3 rounded border border-white/5 leading-relaxed">{proposal.payload.body}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col items-end gap-3 min-w-[200px] border-t border-white/10 pt-4 md:border-t-0 md:border-l md:pt-0 md:pl-6">
                    {proposal.status === 'PENDING_APPROVAL' && (
                      <div className="flex w-full flex-col gap-2">
                        <Button 
                          onClick={() => handleAction(proposal.id, "approve")}
                          disabled={activeAction === `${proposal.id}:approve`}
                          className="w-full bg-green-500 hover:bg-green-600 text-white"
                          isLoading={activeAction === `${proposal.id}:approve`}
                        >
                          Approve Action
                        </Button>
                        <Button 
                          variant="secondary"
                          onClick={() => handleAction(proposal.id, "reject")}
                          disabled={activeAction === `${proposal.id}:reject`}
                          className="w-full hover:bg-error/20 hover:text-error hover:border-error/50"
                          isLoading={activeAction === `${proposal.id}:reject`}
                        >
                          Reject
                        </Button>
                      </div>
                    )}
                    
                    {proposal.status === 'APPROVED' && (
                      <div className="w-full">
                        <Button 
                          onClick={() => handleAction(proposal.id, "execute")}
                          disabled={activeAction === `${proposal.id}:execute`}
                          className="w-full bg-accent-blue hover:bg-blue-600 shadow-[0_0_15px_rgba(59,130,246,0.3)]"
                          leftIcon={<Play size={16} />}
                          isLoading={activeAction === `${proposal.id}:execute`}
                        >
                          Execute Now
                        </Button>
                      </div>
                    )}
                    
                    {proposal.status === 'EXECUTED' && (
                      <div className="flex w-full flex-col items-center justify-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                        <CheckCircle2 className="text-green-400 mb-2" size={24} />
                        <span className="text-green-400 font-semibold text-sm uppercase tracking-widest">Executed</span>
                        {proposal.execution_result && (
                          <div className="mt-2 text-center text-xs text-green-400/80">
                            {proposal.execution_result.message}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {proposal.execution_error && (
                      <div className="mt-4 w-full rounded border border-error/30 bg-error/10 p-3 text-xs text-error">
                        <span className="font-bold block mb-1">Execution Failed:</span>
                        {proposal.execution_error}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
