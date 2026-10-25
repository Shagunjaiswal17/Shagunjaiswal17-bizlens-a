import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, CreditCard, Receipt, Sparkles, Loader2 } from 'lucide-react';

export default function UploadZone({ docType, setDocType, onSelectPreset, onUploadFile, isScanning }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  return (
    <div className="space-y-4">
      {/* Interactive Document Type Selector Tabs */}
      <div className="p-1.5 rounded-xl bg-slate-900/90 border border-slate-800 flex space-x-1 shadow-lg">
        {[
          { id: 'invoice', label: 'Invoice', Icon: FileText },
          { id: 'card', label: 'Business Card', Icon: CreditCard },
          { id: 'receipt', label: 'Tax Receipt', Icon: Receipt },
        ].map(({ id, label, Icon }) => (
          <button
            key={id}
            disabled={isScanning}
            onClick={() => { setDocType(id); onSelectPreset(id); }}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all ${
              docType === id
                ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-md shadow-cyan-500/25 border border-cyan-400/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            } ${isScanning ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Preset Sample Buttons for Hackathon Judges */}
      <div className="bg-slate-900/60 border border-slate-800/90 rounded-xl p-3.5 shadow-md">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Preset Benchmark Samples
          </span>
          <span className="text-[10px] text-cyan-400 font-mono">1-Click Test</span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <button
            disabled={isScanning}
            onClick={() => onSelectPreset('invoice')}
            className={`py-2 px-2 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700/80 text-slate-200 border border-slate-700/60 hover:border-cyan-500/50 transition-all text-center flex flex-col items-center justify-center gap-0.5 ${
              isScanning ? 'opacity-60 cursor-not-allowed' : 'active:scale-95'
            }`}
          >
            <span className="text-cyan-400 font-bold">Sample Invoice</span>
            <span className="text-[10px] text-slate-400">AWS / Cloud</span>
          </button>
          <button
            disabled={isScanning}
            onClick={() => onSelectPreset('card')}
            className={`py-2 px-2 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700/80 text-slate-200 border border-slate-700/60 hover:border-cyan-500/50 transition-all text-center flex flex-col items-center justify-center gap-0.5 ${
              isScanning ? 'opacity-60 cursor-not-allowed' : 'active:scale-95'
            }`}
          >
            <span className="text-indigo-400 font-bold">Business Card</span>
            <span className="text-[10px] text-slate-400">Dr. Vance (CTO)</span>
          </button>
          <button
            disabled={isScanning}
            onClick={() => onSelectPreset('receipt')}
            className={`py-2 px-2 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700/80 text-slate-200 border border-slate-700/60 hover:border-cyan-500/50 transition-all text-center flex flex-col items-center justify-center gap-0.5 ${
              isScanning ? 'opacity-60 cursor-not-allowed' : 'active:scale-95'
            }`}
          >
            <span className="text-emerald-400 font-bold">Tax Receipt</span>
            <span className="text-[10px] text-slate-400">Blue Bottle</span>
          </button>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); if (!isScanning) setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragOver(false);
          if (!isScanning && e.dataTransfer.files?.[0]) {
            onUploadFile(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => {
          if (!isScanning) fileInputRef.current?.click();
        }}
        className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-all duration-300 group ${
          isScanning ? 'opacity-60 cursor-not-allowed border-slate-800 bg-slate-950/40' : 'cursor-pointer'
        } ${
          isDragOver
            ? 'border-cyan-400 bg-cyan-950/20 shadow-lg shadow-cyan-500/20'
            : 'border-slate-700/80 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-900/70'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          disabled={isScanning}
          accept="image/png,image/jpeg,image/webp,application/pdf"
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.[0]) onUploadFile(e.target.files[0]);
          }}
        />
        <div className="w-12 h-12 mx-auto rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          {isScanning ? (
            <Loader2 className="w-6 h-6 text-cyan-400 animate-spin" />
          ) : (
            <UploadCloud className="w-6 h-6 text-cyan-400" />
          )}
        </div>
        <h3 className="text-sm font-semibold text-slate-200">
          {isScanning ? (
            <span className="text-cyan-400 font-mono">Processing with Gemini 1.5 Flash...</span>
          ) : (
            <>Drop document here or <span className="text-cyan-400 underline decoration-cyan-400/50">browse</span></>
          )}
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Supports PNG, JPG, WEBP, or PDF
        </p>
      </div>
    </div>
  );
}
