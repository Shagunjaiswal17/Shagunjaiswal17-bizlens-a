import React from 'react';

export default function MetricsBar({ metrics }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Processing Time</span>
        <span className="text-base font-bold text-cyan-400 font-mono">{metrics.processingTime}</span>
      </div>
      <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Confidence Score</span>
        <span className="text-base font-bold text-emerald-400 font-mono">{metrics.confidence}</span>
      </div>
      <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Tokens Processed</span>
        <span className="text-base font-bold text-indigo-400 font-mono">{metrics.tokens}</span>
      </div>
      <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Schema Model</span>
        <span className="text-xs font-semibold text-slate-200 mt-0.5 block truncate">100% Deterministic</span>
      </div>
    </div>
  );
}
