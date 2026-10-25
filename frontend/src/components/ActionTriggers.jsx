import React from 'react';
import { Mail, BookOpen, Receipt, Copy, AlertTriangle } from 'lucide-react';

const formatCurrency = (val, currency = '$') => {
  if (val === null || val === undefined || isNaN(val)) return `${currency}0.00`;
  return `${currency}${Number(val).toFixed(2)}`;
};

const safeStr = (val, fallback = 'N/A') => {
  if (val === null || val === undefined || String(val).trim() === '') return fallback;
  return String(val);
};

export default function ActionTriggers({ docType, data, onShowToast, isScanning }) {
  if (!data) return null;

  const getOutreachEmail = () => {
    const name = safeStr(data?.person_name, 'Executive');
    const company = safeStr(data?.company_name, 'your team');
    const title = safeStr(data?.job_title, 'Leader');
    return `Subject: Strategic Partnership: ${company} & BizLens AI Architecture\n\nHi ${name},\n\nI noticed your impactful leadership as ${title} at ${company}. Given your team's focus on high-velocity innovation, I wanted to reach out regarding how our deterministic document-to-insight pipelines eliminate manual invoice, receipt, and contact data reconciliation with 100% schema integrity.\n\nWould you be open to a 10-minute briefing next Tuesday at 2:00 PM PST?\n\nBest regards,\nBizLens AI Enterprise Strategy Team\nhttps://bizlens.ai`;
  };

  const handleCopy = () => {
    if (isScanning) return;
    const textToCopy = docType === 'card' ? getOutreachEmail() : JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(textToCopy);
    if (onShowToast) {
      onShowToast(
        docType === 'card' ? 'Outreach Draft Copied!' : 'Ledger Entry Copied!',
        'Saved to system clipboard for instant dispatch'
      );
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-5 shadow-xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between pb-3 mb-3 border-b border-indigo-500/20">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/20 text-cyan-300">
            {docType === 'card' && <Mail className="w-4 h-4" />}
            {docType === 'invoice' && <BookOpen className="w-4 h-4" />}
            {docType === 'receipt' && <Receipt className="w-4 h-4" />}
          </div>
          <div>
            <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
              {docType === 'card' && 'Automated B2B Outreach Generator'}
              {docType === 'invoice' && 'Dual-Entry Accounting Ledger Preview'}
              {docType === 'receipt' && 'Tax Ledger & IRS Expense Classification'}
            </h3>
            <p className="text-[11px] text-slate-400">Autonomous workflow trigger ready for ERP / CRM sync</p>
          </div>
        </div>

        <button
          disabled={isScanning}
          onClick={handleCopy}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-400/30 transition-all active:scale-95 ${
            isScanning ? 'opacity-60 cursor-not-allowed' : ''
          }`}
        >
          <Copy className="w-3.5 h-3.5" />
          <span>{docType === 'card' ? 'Copy Email' : 'Sync Ledger'}</span>
        </button>
      </div>

      {/* Card Action View */}
      {docType === 'card' && (
        <div className="bg-slate-950/80 rounded-xl p-3.5 border border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
          {getOutreachEmail()}
        </div>
      )}

      {/* Invoice Action View */}
      {docType === 'invoice' && (
        <div className="space-y-2.5">
          <div className="flex items-center justify-between p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300">
            <span className="font-semibold flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Payment Due Alert: Net-30 Payment window expires in 24 days
            </span>
            <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-amber-500/20">Auto-Approval Queued</span>
          </div>

          <div className="bg-slate-950/80 rounded-xl p-3 border border-slate-800 font-mono text-xs text-slate-300 space-y-1.5">
            <div className="text-[10px] text-slate-500 border-b border-slate-800 pb-1 flex justify-between">
              <span>ACCOUNT CODE / TITLE</span>
              <span>DEBIT / CREDIT (USD)</span>
            </div>
            <div className="flex justify-between text-cyan-300">
              <span>DR 5200 - Cloud Compute &amp; Infrastructure</span>
              <span>{formatCurrency(data?.subtotal, '$')}</span>
            </div>
            <div className="flex justify-between text-cyan-300">
              <span>DR 1400 - Input Sales Tax Receivable</span>
              <span>{formatCurrency(data?.tax_amount, '$')}</span>
            </div>
            <div className="flex justify-between text-emerald-400 font-bold border-t border-slate-800 pt-1">
              <span>CR 2000 - Accounts Payable ({safeStr(data?.vendor_name, 'Vendor')})</span>
              <span>{formatCurrency(data?.total_amount, '$')}</span>
            </div>
          </div>
        </div>
      )}

      {/* Receipt Action View */}
      {docType === 'receipt' && (
        <div className="bg-slate-950/80 rounded-xl p-3.5 border border-slate-800 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Expense Policy Allocation:</span>
            <span className="font-bold text-cyan-300 font-mono">100% Tax Deductible (Section 162)</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Target GL Category:</span>
            <span className="font-mono text-slate-200">#6420 - Office Kitchen &amp; Consumables</span>
          </div>
        </div>
      )}
    </div>
  );
}
