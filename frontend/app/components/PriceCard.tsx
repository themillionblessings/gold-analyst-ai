"use client";

interface PriceData {
    asset: string;
    price_oz_24k: number;
    daily_change_oz: number;
    percent_change: string;
}

export interface ValidatedGoldResponse {
    final_price: number;
    source: string;
    anomaly_detected: boolean;
    system_note?: string;
}

export default function PriceCard({ data, validatedData }: { data: PriceData | null, validatedData: ValidatedGoldResponse | null }) {
    if (!data || !validatedData) return <div className="animate-pulse h-32 bg-slate-200 rounded-2xl"></div>;

    const isPositive = data.daily_change_oz >= 0;

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 flex flex-col items-center justify-center shadow-sm hover:shadow-md transition-shadow h-full">
            <div className="text-slate-500 font-medium text-sm tracking-wide uppercase mb-2">Gold Price (Live)</div>
            <div className="text-6xl font-bold text-slate-900 tracking-tight">
                ${validatedData.final_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className={`mt-3 text-lg font-medium px-3 py-1 rounded-full ${isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                {isPositive ? "+" : ""}{data.daily_change_oz.toFixed(2)} ({data.percent_change})
            </div>

            {/* System Audit Badge */}
            <div className="mt-4">
                {validatedData.anomaly_detected ? (
                    <div className="flex items-center text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-full border border-amber-200">
                        ⚠️ Anomaly Auto-Corrected | Source: {validatedData.source}
                    </div>
                ) : (
                    <div className="flex items-center text-xs text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-200">
                        🟢 Live (Audited)
                    </div>
                )}
            </div>
        </div>
    );
}
