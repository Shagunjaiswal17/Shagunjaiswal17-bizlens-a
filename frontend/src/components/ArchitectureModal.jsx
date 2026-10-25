import React from 'react';
import { Layers, X, Cpu, Server, Smartphone, ShieldCheck } from 'lucide-react';

export default function ArchitectureModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-3xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-lg">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">BizLens AI System Matrix &amp; Roadmap</h2>
            <p className="text-xs text-slate-400">Enterprise B2B Architecture Specifications</p>
          </div>
        </div>

        {/* Tech Stack Matrix */}
        <div className="mb-6">
          <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3">
            Core Technical Stack
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="font-bold text-slate-200 block mb-1">Inference Engine</span>
              <p className="text-slate-400">
                <strong className="text-cyan-400">Google Gemini 1.5 Flash</strong> via official <code className="text-indigo-300">google-genai</code> SDK with native <code className="text-indigo-300">response_schema</code> for deterministic schema compliance.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="font-bold text-slate-200 block mb-1">Backend Core</span>
              <p className="text-slate-400">
                <strong className="text-slate-200">Python 3.10+ &amp; FastAPI</strong>, Uvicorn ASGI server, Pydantic v2 strict data modeling, CORS security middleware, and resilient 500 error sanitization.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="font-bold text-slate-200 block mb-1">User Interface</span>
              <p className="text-slate-400">
                Tailwind CSS, React 18 component modularity, Lucide Icons, interactive drag-and-drop, and animated laser scanning viewport.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="font-bold text-slate-200 block mb-1">Fail-Safe Resilience</span>
              <p className="text-slate-400">
                Automatic fallback validation ensures null lists (<code className="text-cyan-300">phone_numbers</code>, <code className="text-cyan-300">line_items</code>) default to empty arrays, preventing frontend crashes.
              </p>
            </div>
          </div>
        </div>

        {/* 6-Month SaaS Roadmap */}
        <div>
          <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-3">
            6-Month Commercial SaaS Roadmap
          </h3>
          <div className="space-y-3">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start space-x-3">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                M1-M2
              </span>
              <div>
                <strong className="text-xs text-slate-200 block">Multi-Page Bounding Box Reconstruction</strong>
                <p className="text-xs text-slate-400 mt-0.5">
                  High-throughput PDF batching, multi-currency conversion, and OCR bounding-box highlights overlaid directly on document coordinates.
                </p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start space-x-3">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                M3-M4
              </span>
              <div>
                <strong className="text-xs text-slate-200 block">Direct ERP Two-Way Reconciliation</strong>
                <p className="text-xs text-slate-400 mt-0.5">
                  Plug-and-play integrations with SAP S/4HANA, QuickBooks Online, Xero, and NetSuite with automated invoice match and discrepancy flagging.
                </p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start space-x-3">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                M5-M6
              </span>
              <div>
                <strong className="text-xs text-slate-200 block">Autonomous Payment &amp; Dispute Resolution Agents</strong>
                <p className="text-xs text-slate-400 mt-0.5">
                  Autonomous AI agents for vendor inquiry resolution, early-payment discount optimization, and SOC2 Type II compliance audit trail.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
          >
            Close Architecture Matrix
          </button>
        </div>
      </div>
    </div>
  );
}
