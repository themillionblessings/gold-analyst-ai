"use client";

import { useState, useEffect } from "react";

interface PriceData {
    usd: Record<string, number>;
    egypt: Record<string, number>;
    uae: Record<string, number>;
}

export default function GoldCalculator({ priceData }: { priceData: PriceData | null }) {
    const [grams, setGrams] = useState<number>(1);
    const [karat, setKarat] = useState<string>("24k");
    const [market, setMarket] = useState<string>("usd");
    const [calculatedPrice, setCalculatedPrice] = useState<number>(0);

    useEffect(() => {
        if (priceData && priceData[market as keyof PriceData] && grams > 0) {
            const marketPrices = priceData[market as keyof PriceData];
            const pricePerGram = marketPrices[karat as keyof typeof marketPrices];
            if (pricePerGram) {
                setCalculatedPrice(pricePerGram * grams);
            }
        }
    }, [grams, karat, market, priceData]);

    if (!priceData) return null;

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow h-full">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Gold Value Calculator</h2>

            <div className="space-y-6">
                {/* Input Group */}
                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Weight (Grams)</label>
                        <input
                            type="number"
                            value={grams}
                            onChange={(e) => setGrams(parseFloat(e.target.value) || 0)}
                            className="w-full bg-[#F5F5F7] text-slate-900 font-bold border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-emerald-500/20 outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Market & Karat</label>
                        <div className="flex gap-2">
                            <select
                                value={market}
                                onChange={(e) => setMarket(e.target.value)}
                                className="w-1/2 bg-[#F5F5F7] text-slate-900 font-medium border-none rounded-2xl px-4 py-3 outline-none"
                            >
                                <option value="usd">USD ($)</option>
                                <option value="egypt">Egypt (EGP)</option>
                                <option value="uae">UAE (AED)</option>
                            </select>
                            <select
                                value={karat}
                                onChange={(e) => setKarat(e.target.value)}
                                className="w-1/2 bg-[#F5F5F7] text-slate-900 font-medium border-none rounded-2xl px-4 py-3 outline-none"
                            >
                                <option value="24k">24k</option>
                                <option value="21k">21k</option>
                                <option value="18k">18k</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Result */}
                <div className="pt-6 border-t border-slate-100 mt-2">
                    <div className="text-center">
                        <div className="text-sm text-slate-500 mb-1">Estimated Value</div>
                        <div className="text-4xl font-bold text-emerald-600 tracking-tight">
                            {market === "usd" ? "$" : market === "egypt" ? "EGP " : "AED "}
                            {calculatedPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
