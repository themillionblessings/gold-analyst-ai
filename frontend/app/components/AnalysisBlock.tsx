"use client";

import { useState } from "react";

interface AnalysisResponse {
    recommendation: string;
    confidence: number;
    rationale_brief: string;
    rationale_technical: string;
    suggested_risk_tier: string;
    final_action: string;
}

export default function AnalysisBlock() {
    const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchAnalysis = async () => {
        setLoading(true);
        try {
            // Hardcoded dummy payload for now as requested for MVP connectivity
            const payload = {
                price: 2600.00,
                change_percent: 1.5,
                gld_data: { price: 245.00, timestamp_utc: new Date().toISOString() },
                xau_data: { price: 2600.00 }
            };

            const res = await fetch("http://localhost:8000/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const json = await res.json();
            setAnalysis(json);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getActionColor = (action: string) => {
        if (action === "BUY") return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
        if (action === "SELL") return "text-rose-400 border-rose-500/30 bg-rose-500/10";
        return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    };

    return (
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-white">AI Analysis</h2>
                <button
                    onClick={fetchAnalysis}
                    disabled={loading}
                    className="bg-white text-slate-900 hover:bg-slate-200 px-4 py-2 rounded-full font-medium text-sm transition-all disabled:opacity-50"
                >
                    {loading ? "Analyzing..." : "Generate Analysis"}
                </button>
            </div>

            {analysis ? (
                <div className="flex-1 flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className={`p-6 rounded-2xl border flex flex-col items-center justify-center text-center ${getActionColor(analysis.final_action)}`}>
                        <div className="text-5xl font-bold tracking-tighter">{analysis.final_action}</div>
                        <div className="mt-2 opacity-80 font-medium">Confidence: {analysis.confidence}%</div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Brief Rationale</div>
                            <div className="text-slate-200 text-lg leading-snug">{analysis.rationale_brief}</div>
                        </div>
                        <div>
                            <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Technical Deep Dive</div>
                            <div className="text-slate-400 text-sm leading-relaxed">{analysis.rationale_technical}</div>
                        </div>
                        <div className="pt-4 border-t border-slate-700/50 flex justify-between items-center">
                            <span className="text-slate-400 text-sm">Risk Tier</span>
                            <span className="text-white font-medium bg-slate-700/50 px-3 py-1 rounded-lg">{analysis.suggested_risk_tier}</span>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex-1 flex items-center justify-center text-slate-500 text-sm italic">
                    Click generate to start AI analysis
                </div>
            )}
        </div>
    );
}
