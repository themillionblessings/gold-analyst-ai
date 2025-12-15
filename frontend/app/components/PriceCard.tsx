"use client";

import { useEffect, useState } from "react";

interface PriceData {
    asset: string;
    price_oz_24k: number;
    daily_change_oz: number;
    percent_change: string;
}

export default function PriceCard() {
    const [data, setData] = useState<PriceData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchPrice() {
            try {
                const res = await fetch("http://localhost:8000/price/GC=F");
                const json = await res.json();
                setData(json);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        fetchPrice();
        const interval = setInterval(fetchPrice, 60000); // Update every minute
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="animate-pulse h-32 bg-slate-800 rounded-2xl"></div>;
    if (!data) return <div className="text-red-400">Error loading price</div>;

    const isPositive = data.daily_change_oz >= 0;

    return (
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 flex flex-col items-center justify-center shadow-2xl">
            <div className="text-slate-400 font-medium text-sm tracking-wide uppercase mb-2">Gold Price (Live)</div>
            <div className="text-6xl font-bold text-white tracking-tight">
                ${data.price_oz_24k.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className={`mt-3 text-lg font-medium px-3 py-1 rounded-full ${isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                {isPositive ? "+" : ""}{data.daily_change_oz.toFixed(2)} ({data.percent_change})
            </div>
        </div>
    );
}
