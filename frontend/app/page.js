'use client';
import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  async function fetchStats() {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      setStats(await res.json());
    } catch (e) {}
  }

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 4000);
    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const query = input;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: query }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: data.response, blocked: !!data.blocked_at, blockedAt: data.blocked_at, traceId: data.trace_id },
      ]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'assistant', text: 'Could not reach the API — is the backend running?', blocked: true }]);
    } finally {
      setLoading(false);
      fetchStats();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-slate-800 flex">
      {/* Chat panel */}
      <div className="flex-1 flex flex-col max-w-2xl mx-auto py-10 px-6">
        <h1 className="text-xl font-semibold text-slate-900 mb-1">Internal Knowledge Assistant</h1>
        <p className="text-sm text-slate-500 mb-6">Answers are grounded in company docs and checked by a guardrail pipeline before you see them.</p>

        <div className="flex-1 space-y-4 overflow-y-auto mb-4">
          {messages.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
              <div
                className={`max-w-md rounded-2xl px-4 py-2.5 text-sm ${
                  m.role === 'user'
                    ? 'bg-violet-600 text-white'
                    : m.blocked
                    ? 'bg-red-50 border border-red-200 text-red-700'
                    : 'bg-white border border-gray-200 text-slate-700'
                }`}
              >
                {m.text}
                {m.role === 'assistant' && (
                  <div className="mt-1.5 font-mono text-[10px] opacity-50">
                    {m.blocked ? `blocked at: ${m.blockedAt}` : `trace: ${m.traceId?.slice(0, 8)}`}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-sm text-slate-400">thinking…</div>}
        </div>

        <div className="flex gap-2">
          <input
            className="flex-1 rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about company policy..."
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="rounded-xl bg-violet-600 text-white px-5 py-2.5 text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>

      {/* Security panel — the signature element */}
      <div className="w-80 border-l border-gray-200 bg-white py-10 px-5">
        <div className="flex items-center gap-2 mb-4">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <h2 className="text-sm font-semibold text-slate-900">Guardrail Activity</h2>
        </div>

        {stats ? (
          <>
            <div className="grid grid-cols-2 gap-3 mb-6">
              <StatCard label="Input checks" total={stats.input_guardrail.total} blocked={stats.input_guardrail.blocked} />
              <StatCard label="Output checks" total={stats.output_guardrail.total} blocked={stats.output_guardrail.blocked} />
            </div>

            <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">Recent events</h3>
            <div className="space-y-2">
              {stats.recent_events.length === 0 && <p className="text-xs text-slate-400">No activity yet.</p>}
              {stats.recent_events.map((e, i) => (
                <div key={i} className={`rounded-lg border px-3 py-2 text-xs ${e.blocked ? 'border-red-200 bg-red-50' : 'border-gray-100 bg-gray-50'}`}>
                  <div className="flex justify-between font-mono text-[10px] text-slate-400">
                    <span>{e.stage.replace('_guardrail', '')}</span>
                    <span>{e.latency_ms}ms</span>
                  </div>
                  <div className={e.blocked ? 'text-red-700 font-medium' : 'text-slate-600'}>{e.blocked ? 'Blocked' : 'Passed'}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-xs text-slate-400">Connecting to API...</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, total, blocked }) {
  return (
    <div className="rounded-xl bg-gray-50 border border-gray-100 px-3 py-2.5">
      <div className="text-[11px] text-slate-400">{label}</div>
      <div className="text-lg font-semibold text-slate-900">{total}</div>
      <div className="text-[11px] text-red-500">{blocked} blocked</div>
    </div>
  );
}