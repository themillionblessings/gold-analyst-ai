"use client";

interface PriceData {
    asset: string;
    price_oz_24k: number;
    daily_change_oz: number;
    percent_change: string;
}

export default function PriceCard({ data }: { data: PriceData | null }) {
    if (!data) return <div className="animate-pulse h-32 bg-slate-200 rounded-2xl"></div>;

    const isPositive = data.daily_change_oz >= 0;

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 flex flex-col items-center justify-center shadow-sm hover:shadow-md transition-shadow h-full">
            <div className="text-slate-500 font-medium text-sm tracking-wide uppercase mb-2">Gold Price (Live)</div>
            <div className="text-6xl font-bold text-slate-900 tracking-tight">
                ${data.price_oz_24k.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className={`mt - 3 text - lg font - medium px - 3 py - 1 rounded - full ${isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'} `}>
                {isPositive ? "+" : ""}{data.daily_change_oz.toFixed(2)} ({data.percent_change})
            </div>
        </div>
    );
}

