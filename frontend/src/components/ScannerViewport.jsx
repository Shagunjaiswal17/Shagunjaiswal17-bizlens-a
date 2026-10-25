import React from 'react';

export default function ScannerViewport({ previewUrl, isScanning }) {
  return (
    <div className="relative rounded-2xl bg-slate-900/80 border border-slate-800 p-3 overflow-hidden shadow-2xl">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-xs text-slate-400 font-mono">
        <span>ACTIVE DOCUMENT SOURCE</span>
        <span className="text-cyan-400 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
          Resolution Scaled
        </span>
      </div>

      <div className="relative rounded-xl overflow-hidden bg-slate-950 min-h-[300px] flex items-center justify-center border border-slate-800/80">
        {/* Animated Glowing Laser Scanner Bar */}
        {isScanning && (
          <div className="absolute inset-0 pointer-events-none z-30 overflow-hidden">
            <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-indigo-500 shadow-[0_0_15px_3px_#22d3ee] animate-scan" />
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 to-transparent pointer-events-none" />
          </div>
        )}

        {/* Document Image */}
        <img
          src={previewUrl}
          alt="Active Document"
          className="w-full h-auto max-h-[380px] object-contain rounded-lg transition-opacity duration-300"
        />

        {/* Scanning Badge Overlay */}
        {isScanning && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-40 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-cyan-500/50 backdrop-blur-md flex items-center space-x-2 text-xs text-cyan-300 font-mono shadow-lg shadow-cyan-500/20">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>Gemini 1.5 Flash Scanning...</span>
          </div>
        )}
      </div>
    </div>
  );
}
