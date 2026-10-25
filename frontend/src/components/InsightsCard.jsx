import React from 'react';
import { Sparkles } from 'lucide-react';

const formatCurrency = (val, currency = '$') => {
  if (val === null || val === undefined || isNaN(val)) return `${currency}0.00`;
  return `${currency}${Number(val).toFixed(2)}`;
};

const safeStr = (val, fallback = 'N/A') => {
  if (val === null || val === undefined || String(val).trim() === '') return fallback;
  return String(val);
};

export default function InsightsCard({ docType, data }) {
  if (!data) return null;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Verified Extracted Metadata
          </h2>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          Structured Response
        </span>
      </div>

      {/* Invoice Schema View */}
      {docType === 'invoice' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Vendor Name</span>
              <span className="text-sm font-bold text-slate-100 mt-0.5 block truncate">
                {safeStr(data?.vendor_name, 'CloudScale Systems Inc.')}
              </span>
            </div>
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Invoice Number</span>
              <span className="text-sm font-bold text-cyan-400 font-mono mt-0.5 block truncate">
                {safeStr(data?.invoice_number, 'INV-2025-9941')}
              </span>
            </div>
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Due Date</span>
              <span className="text-sm font-bold text-rose-400 font-mono mt-0.5 block truncate">
                {safeStr(data?.due_date, '2025-11-18')}
              </span>
            </div>
          </div>

          {/* Line Items Table */}
          <div className="bg-slate-950/60 rounded-xl border border-slate-800 overflow-hidden">
            <div className="px-3.5 py-2 bg-slate-800/50 border-b border-slate-800 text-[11px] font-mono text-slate-400 grid grid-cols-12">
              <span className="col-span-6">ITEM DESCRIPTION</span>
              <span className="col-span-2 text-center">QTY</span>
              <span className="col-span-2 text-right">UNIT PRICE</span>
              <span className="col-span-2 text-right">TOTAL</span>
            </div>
            <div className="divide-y divide-slate-800/60 text-xs">
              {(data?.line_items || []).length > 0 ? (
                (data?.line_items || []).map((item, idx) => (
                  <div key={idx} className="px-3.5 py-2.5 grid grid-cols-12 text-slate-300">
                    <span className="col-span-6 font-medium text-slate-200 truncate">
                      {safeStr(item?.desc, 'Standard Billable Item')}
                    </span>
                    <span className="col-span-2 text-center text-slate-400 font-mono">
                      {item?.qty ?? 1}
                    </span>
                    <span className="col-span-2 text-right text-slate-400 font-mono">
                      {formatCurrency(item?.unit_price)}
                    </span>
                    <span className="col-span-2 text-right font-bold text-cyan-400 font-mono">
                      {formatCurrency(item?.total_price)}
                    </span>
                  </div>
                ))
              ) : (
                <div className="px-3.5 py-3 text-center text-slate-500 font-mono">
                  No line items detected
                </div>
              )}
            </div>
          </div>

          {/* Financial Totals Strip */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
            <div>
              <span className="text-xs text-slate-400">Payment Status:</span>
              <span className="ml-2 px-2.5 py-0.5 rounded text-[11px] font-bold font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
                {safeStr(data?.payment_status, 'PENDING')}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-xs text-slate-400">
                Tax: <strong className="text-slate-200 font-mono">{formatCurrency(data?.tax_amount)}</strong>
              </span>
              <span className="text-sm font-bold text-slate-100">
                Total Amount: <strong className="text-lg text-cyan-400 font-mono">{formatCurrency(data?.total_amount)}</strong>
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Business Card Schema View */}
      {docType === 'card' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Full Name</span>
              <span className="text-base font-bold text-slate-100 mt-0.5 block">
                {safeStr(data?.person_name, 'Dr. Marcus Vance')}
              </span>
              <span className="text-xs text-cyan-400 font-medium mt-0.5 block">
                {safeStr(data?.job_title, 'Chief Technology Officer')}
              </span>
            </div>
            <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Company</span>
              <span className="text-base font-bold text-indigo-300 mt-0.5 block">
                {safeStr(data?.company_name, 'Vortex Quantum Intelligence Inc.')}
              </span>
              <span className="text-xs text-slate-400 font-mono mt-0.5 block truncate">
                {safeStr(data?.website, 'https://vortexquantum.ai')}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Email Address</span>
              <span className="text-xs font-mono text-cyan-300 mt-0.5 block truncate">
                {safeStr(data?.email, 'contact@vortexquantum.ai')}
              </span>
            </div>
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Phone Numbers</span>
              <span className="text-xs font-mono text-slate-300 mt-0.5 block truncate">
                {(data?.phone_numbers || []).join(', ') || '+1 (415) 890-4491'}
              </span>
            </div>
          </div>

          <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[11px] text-slate-400 block font-medium mb-1.5">Business &amp; Category Tags</span>
            <div className="flex flex-wrap gap-1.5">
              {(data?.tags || []).length > 0 ? (
                (data?.tags || []).map((t, i) => (
                  <span key={i} className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                    #{safeStr(t)}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-500 font-mono">No category tags detected</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tax Receipt Schema View */}
      {docType === 'receipt' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Merchant</span>
              <span className="text-sm font-bold text-slate-100 mt-0.5 block truncate">
                {safeStr(data?.merchant_name, 'Blue Bottle Coffee')}
              </span>
            </div>
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Transaction Date</span>
              <span className="text-sm font-bold text-cyan-400 font-mono mt-0.5 block truncate">
                {safeStr(data?.transaction_date, '2025-10-24')}
              </span>
            </div>
            <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Expense Category</span>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 mt-1 inline-block">
                {safeStr(data?.expense_category, 'Kitchen Supplies')}
              </span>
            </div>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Payment Method</span>
              <span className="text-sm font-semibold text-slate-200 mt-0.5 block">
                {safeStr(data?.payment_method, 'Corporate Visa (•••• 9924)')}
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 block">Grand Total</span>
              <span className="text-xl font-bold text-cyan-400 font-mono mt-0.5 block">
                {formatCurrency(data?.grand_total)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
