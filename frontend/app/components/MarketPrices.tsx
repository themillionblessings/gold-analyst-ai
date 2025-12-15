"use client";

import { useEffect, useState } from "react";

interface PriceData {
    usd: Record<string, number>;
    egypt: Record<string, number>;
    uae: Record<string, number>;
}

export default function MarketPrices({ priceData }: { priceData: PriceData | null }) {
    if (!priceData) return <div className="h-64 bg-slate-50 rounded-3xl animate-pulse"></div>;

    const markets = [
        { name: "Global (USD)", currency: "$", data: priceData.usd, flag: "🌍" },
        { name: "Egypt (EGP)", currency: "EGP", data: priceData.egypt, flag: "🇪🇬" },
        { name: "UAE (AED)", currency: "AED", data: priceData.uae, flag: "🇦🇪" },
    ];

    const keys = ["24k", "21k", "18k", "Troy Ounce"];

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Market Prices</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {markets.map((market) => (
                    <div key={market.name} className="flex flex-col gap-3">
                        <div className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-1 flex items-center gap-2">
                            <span>{market.flag}</span> {market.name}
                        </div>
                        <div className="space-y-2">
                            {keys.map((key) => (
                                <div key={key} className="flex justify-between items-center p-3 bg-slate-50 rounded-xl border border-slate-100">
                                    <span className="text-sm font-medium text-slate-600">{key}</span>
                                    <span className="text-sm font-bold text-slate-900 font-mono">
                                        {market.currency} {market.data[key]?.toLocaleString()}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
