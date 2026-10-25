import React from 'react';
import { Check, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slide-up flex items-center space-x-3 px-4 py-3 rounded-xl bg-slate-900/95 border border-cyan-500/50 text-slate-100 shadow-2xl shadow-cyan-500/25 backdrop-blur-xl">
      <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center text-cyan-400">
        <Check className="w-4 h-4" />
      </div>
      <div>
        <h4 className="text-xs font-bold text-slate-100">{toast.title}</h4>
        <p className="text-[11px] text-slate-400">{toast.message}</p>
      </div>
      <button
        onClick={onClose}
        className="text-slate-400 hover:text-white ml-2 p-1 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
