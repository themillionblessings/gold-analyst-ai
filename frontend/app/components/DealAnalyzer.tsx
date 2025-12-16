"use client";

import { useState, useEffect } from "react";

interface DealAnalyzerProps {
    priceData: any;
}

export default function DealAnalyzer({ priceData }: DealAnalyzerProps) {
    const [market, setMarket] = useState("uae");
    const [itemType, setItemType] = useState("bullion"); // bullion | jewelry
    const [karat, setKarat] = useState("24k");
    const [weight, setWeight] = useState(1);
    const [offeredPrice, setOfferedPrice] = useState(0);

    const [result, setResult] = useState<any>(null);

    // Constants for thresholds
    const THRESHOLDS = {
        bullion: { great: 2.5, good: 5.0, fair: 9.0 },
        jewelry: { great: 15.0, good: 25.0, fair: 35.0 },
    };

    useEffect(() => {
        if (!priceData || !offeredPrice || !weight) {
            setResult(null);
            return;
        }

        // 1. Get Price Per Gram
        let pricePerGram = 0;
        let currency = "";

        if (market === "international") {
            currency = "USD";
            // data.usd["24k"], etc.
            // Need to handle missing keys or map them correctly
            // priceData.usd is { "24k": ..., "21k": ... }
            pricePerGram = priceData.usd?.[karat] || 0;
        } else if (market === "uae") {
            currency = "AED";
            pricePerGram = priceData.uae?.[karat] || 0;
        } else if (market === "egypt") {
            currency = "EGP";
            pricePerGram = priceData.egypt?.[karat] || 0;
        }

        if (!pricePerGram) return;

        // 2. Calculate Intrinsic Value
        const intrinsicValue = weight * pricePerGram;

        // 3. Premium
        const premiumAmount = offeredPrice - intrinsicValue;
        const premiumPercent = (premiumAmount / intrinsicValue) * 100;

        // 4. Verdict
        let verdict = "";
        let verdictColor = "";
        const t = itemType === "bullion" ? THRESHOLDS.bullion : THRESHOLDS.jewelry;

        if (premiumPercent <= t.great) {
            verdict = "Great Deal! 💎";
            verdictColor = "text-emerald-600";
        } else if (premiumPercent <= t.good) {
            verdict = "Good Deal ✅";
            verdictColor = "text-green-600";
        } else if (premiumPercent <= t.fair) {
            verdict = "Fair Price ⚖️";
            verdictColor = "text-yellow-600";
        } else {
            verdict = "Too High 🛑";
            verdictColor = "text-red-600";
        }

        setResult({
            currency,
            intrinsicValue,
            premiumAmount,
            premiumPercent,
            verdict,
            verdictColor
        });

    }, [market, itemType, karat, weight, offeredPrice, priceData]);

    // Handle Karat Options based on Market/Type
    // For bullion, usually 24k. For jewelry 18k/21k.
    // But let's keep all options open for simplicity unless requested.

    return (
        <div className="bg-white/60 backdrop-blur-xl border border-white/20 rounded-3xl p-6 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-100/50 rounded-2xl text-blue-600">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                </div>
                <div>
                    <h2 className="text-lg font-semibold text-slate-800">Smart Deal Evaluator</h2>
                    <p className="text-sm text-slate-500">Calculate premiums & rate offers</p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
                {/* Market Selector */}
                <div className="col-span-1">
                    <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Market</label>
                    <select
                        value={market}
                        onChange={(e) => setMarket(e.target.value)}
                        className="w-full bg-[#F5F5F7] border-0 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-700 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                    >
                        <option value="uae">🇦🇪 UAE (AED)</option>
                        <option value="egypt">🇪🇬 Egypt (EGP)</option>
                        <option value="international">🌍 Global (USD)</option>
                    </select>
                </div>

                {/* Item Type */}
                <div className="col-span-1">
                    <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Item Type</label>
                    <select
                        value={itemType}
                        onChange={(e) => setItemType(e.target.value)}
                        className="w-full bg-[#F5F5F7] border-0 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-700 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                    >
                        <option value="bullion">📀 Bullion/Bar</option>
                        <option value="jewelry">💍 Jewelry</option>
                    </select>
                </div>

                {/* Karat */}
                <div className="col-span-1">
                    <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Karat</label>
                    <select
                        value={karat}
                        onChange={(e) => setKarat(e.target.value)}
                        className="w-full bg-[#F5F5F7] border-0 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-700 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                    >
                        <option value="24k">24k (999)</option>
                        <option value="22k">22k (916)</option>
                        <option value="21k">21k (875)</option>
                        <option value="18k">18k (750)</option>
                    </select>
                </div>

                {/* Weight */}
                <div className="col-span-1">
                    <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Weight (g)</label>
                    <input
                        type="number"
                        value={weight}
                        onChange={(e) => setWeight(parseFloat(e.target.value))}
                        className="w-full bg-[#F5F5F7] border-0 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-700 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                        placeholder="0.00"
                    />
                </div>

                {/* Offer Price */}
                <div className="col-span-2">
                    <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Offered Total Price</label>
                    <div className="relative">
                        <input
                            type="number"
                            value={offeredPrice || ""}
                            onChange={(e) => setOfferedPrice(parseFloat(e.target.value))}
                            className="w-full bg-[#F5F5F7] border-0 rounded-xl pl-4 pr-16 py-3 text-lg font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none placeholder:text-slate-300"
                            placeholder="Total Cost"
                        />
                        <div className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-slate-400">
                            {market === "uae" ? "AED" : market === "egypt" ? "EGP" : "USD"}
                        </div>
                    </div>
                </div>
            </div>

            {/* Results */}
            {result && result.intrinsicValue > 0 && offeredPrice > 0 ? (
                <div className="space-y-4 pt-4 border-t border-slate-100">

                    <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-500">Real Gold Value</span>
                        <span className="text-sm font-semibold text-slate-700">
                            {result.intrinsicValue.toLocaleString(undefined, { maximumFractionDigits: 1 })} {result.currency}
                        </span>
                    </div>

                    <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-500">Premium Added</span>
                        <div className="text-right">
                            <span className={`block text-sm font-bold ${result.premiumAmount > 0 ? "text-red-500" : "text-green-500"}`}>
                                {result.premiumAmount > 0 ? "+" : ""}{result.premiumAmount.toLocaleString(undefined, { maximumFractionDigits: 1 })} {result.currency}
                            </span>
                            <span className="text-xs text-slate-400">
                                ({result.premiumPercent.toFixed(1)}%)
                            </span>
                        </div>
                    </div>

                    <div className="mt-4 p-4 bg-slate-50 rounded-2xl flex items-center justify-between">
                        <span className="text-sm font-medium text-slate-500">Verdict</span>
                        <span className={`text-xl font-bold ${result.verdictColor}`}>
                            {result.verdict}
                        </span>
                    </div>

                </div>
            ) : (
                <div className="text-center pt-8 pb-4 text-slate-400 text-sm">
                    Enter details to evaluate deal
                </div>
            )}
        </div>
    );
}
