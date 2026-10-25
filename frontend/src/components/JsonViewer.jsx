import React from 'react';
import { Copy, Code } from 'lucide-react';

export default function JsonViewer({ data, onShowToast, isScanning }) {
  const handleCopy = () => {
    if (isScanning || !data) return;
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    if (onShowToast) {
      onShowToast('JSON Copied to Clipboard!', 'Pydantic v2 structured output ready for API ingestion');
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-xl">
      <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold text-slate-300 font-mono flex items-center gap-1.5">
            <Code className="w-4 h-4 text-cyan-400" />
            DETERMINISTIC JSON OUTPUT (PYDANTIC V2)
          </span>
        </div>
        <button
          disabled={isScanning}
          onClick={handleCopy}
          className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all active:scale-95 ${
            isScanning ? 'opacity-60 cursor-not-allowed' : ''
          }`}
        >
          <Copy className="w-3.5 h-3.5" />
          <span>Copy Raw JSON</span>
        </button>
      </div>

      <pre className="bg-slate-950/90 rounded-xl p-3.5 border border-slate-800/80 font-mono text-xs text-cyan-300 overflow-x-auto max-h-60 leading-relaxed">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
