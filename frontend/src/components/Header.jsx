import React from 'react';
import { Sparkles, Layers, Cpu } from 'lucide-react';

export default function Header({ onOpenArchitecture }) {
  return (
    <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-xl sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3.5">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-lg shadow-cyan-500/25">
          <svg className="w-5 h-5 text-white animate-spin-slow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="4" />
            <line x1="4.93" y1="4.93" x2="9.17" y2="9.17" />
            <line x1="14.83" y1="14.83" x2="19.07" y2="19.07" />
            <line x1="14.83" y1="9.17" x2="19.07" y2="4.93" />
            <line x1="4.93" y1="19.07" x2="9.17" y2="14.83" />
          </svg>
          <div className="absolute -inset-0.5 rounded-xl bg-cyan-400 opacity-30 blur-sm -z-10 animate-pulse"></div>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
              BizLens AI
            </h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              v1.0-PROD
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium hidden sm:block">
            Autonomous B2B Document-to-Insight Architecture
          </p>
        </div>
      </div>

      {/* Status & CTA Controls */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        {/* Gemini Active Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/90 border border-slate-700/80 shadow-inner">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <span className="text-cyan-400 font-mono">Gemini 1.5 Flash</span>
            <span className="text-emerald-400 font-bold hidden sm:inline">Active</span>
          </span>
        </div>

        {/* Top CTA Button */}
        <button
          onClick={onOpenArchitecture}
          className="flex items-center space-x-2 px-4 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white shadow-md shadow-indigo-500/20 transition-all duration-200 border border-indigo-400/30 active:scale-95"
        >
          <Layers className="w-4 h-4 text-cyan-200" />
          <span className="hidden md:inline">System Matrix Architecture</span>
          <span className="md:hidden">Architecture</span>
        </button>
      </div>
    </header>
  );
}
