'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

const API_BASE = 'http://localhost:8000';

export default function Landing() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/stats`).then((r) => r.json()).then(setStats).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 text-slate-800">
      {/* Hero */}
      <section className="max-w-3xl mx-auto pt-20 pb-16 px-6 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-violet-50 border border-violet-200 px-3 py-1 text-xs font-medium text-violet-700 mb-6">
          <span className="h-1.5 w-1.5 rounded-full bg-violet-500" />
          Defense-in-depth RAG, not a demo
        </div>
        <h1 className="text-4xl font-bold text-slate-900 mb-4 tracking-tight">
          A RAG system that assumes<br />someone will try to break it.
        </h1>
        <p className="text-slate-500 max-w-xl mx-auto mb-8">
          Four independent guardrail stages, RBAC-enforced retrieval, and an adversarial
          evaluation harness — mapped to OWASP&apos;s 2025 LLM Top 10 and 2026 Agentic Top 10.
        </p>
        <Link
          href="/chat"
          className="inline-block rounded-xl bg-violet-600 text-white px-6 py-3 text-sm font-medium hover:bg-violet-700 transition"
        >
          Try the live demo →
        </Link>
      </section>

      {/* Pipeline */}
      <section className="max-w-3xl mx-auto px-6 pb-16">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-4">How a request is handled</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {[
            { label: 'Input guardrails', desc: 'Injection + PII scan', color: 'bg-red-50 border-red-200 text-red-700' },
            { label: 'Retrieval', desc: 'Hybrid search + RBAC filter', color: 'bg-violet-50 border-violet-200 text-violet-700' },
            { label: 'Guarded generation', desc: 'Context isolated from data', color: 'bg-violet-50 border-violet-200 text-violet-700' },
            { label: 'Output guardrails', desc: 'Groundedness + PII + toxicity', color: 'bg-red-50 border-red-200 text-red-700' },
          ].map((step, i) => (
            <div key={i} className={`rounded-xl border px-4 py-3 ${step.color}`}>
              <div className="text-xs font-mono opacity-60 mb-1">stage {i + 1}</div>
              <div className="text-sm font-semibold">{step.label}</div>
              <div className="text-xs opacity-70 mt-0.5">{step.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Live stats, if the API happens to be up */}
      {stats && (
        <section className="max-w-3xl mx-auto px-6 pb-20">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-4">Live guardrail activity</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl bg-white border border-gray-200 px-5 py-4">
              <div className="text-xs text-slate-400">Input checks run</div>
              <div className="text-2xl font-semibold text-slate-900">{stats.input_guardrail.total}</div>
              <div className="text-xs text-red-500">{stats.input_guardrail.blocked} blocked</div>
            </div>
            <div className="rounded-xl bg-white border border-gray-200 px-5 py-4">
              <div className="text-xs text-slate-400">Output checks run</div>
              <div className="text-2xl font-semibold text-slate-900">{stats.output_guardrail.total}</div>
              <div className="text-xs text-red-500">{stats.output_guardrail.blocked} blocked</div>
            </div>
          </div>
        </section>
      )}

      <footer className="max-w-3xl mx-auto px-6 pb-16 text-center text-xs text-slate-400">
        Built with FastAPI, Qdrant, Gemini, and Presidio · <a href="#" className="underline hover:text-slate-600">View on GitHub</a>
      </footer>
    </div>
  );
}