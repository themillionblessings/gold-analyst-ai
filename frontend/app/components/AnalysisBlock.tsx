"use client";

import { useState } from "react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer
} from "recharts";

interface AnalysisResponse {
    recommendation: string;
    confidence: number;
    rationale_brief: string;
    rationale_technical: string;
    suggested_risk_tier: string;
    final_action: string;
    dynamic_ui?: {
        component: string;
        data: Array<{ date: string; price: number }>;
    };
}

export default function AnalysisBlock() {
    const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchAnalysis = async () => {
        setLoading(true);
        try {
            // Updated payload to match backend requirements
            const payload = {
                price: 0,
                change_percent: 0,
                gld_data: {},
                xau_data: {}
            };

            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${baseUrl}/analyze`, {
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
        if (action === "BUY") return "text-emerald-600 border-emerald-200 bg-emerald-50";
        if (action === "SELL") return "text-rose-600 border-rose-200 bg-rose-50";
        return "text-amber-600 border-amber-200 bg-amber-50";
    };

    const renderChart = () => {
        if (!analysis?.dynamic_ui || analysis.dynamic_ui.component !== "TrendChart") return null;

        const data = analysis.dynamic_ui.data;
        if (!data || data.length === 0) return null;

        const isUp = data[data.length - 1].price >= data[0].price;
        const color = isUp ? "#10b981" : "#f43f5e"; // emerald-500 or rose-500
        const gradientId = `colorPrice-${isUp ? "up" : "down"}`;

        return (
            <div className="mt-6 h-32 w-full animate-in fade-in duration-1000">
                <div className="text-slate-400 text-[10px] uppercase tracking-widest font-bold mb-2">14-Day Momentum Sparkline</div>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={color} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <Tooltip
                            contentStyle={{
                                borderRadius: '12px',
                                border: 'none',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                                fontSize: '12px'
                            }}
                            labelStyle={{ display: 'none' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="price"
                            stroke={color}
                            strokeWidth={2}
                            fillOpacity={1}
                            fill={`url(#${gradientId})`}
                            dot={false}
                            isAnimationActive={true}
                        />
                        <XAxis dataKey="date" hide />
                        <YAxis hide domain={['auto', 'auto']} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        );
    };

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm h-full flex flex-col hover:shadow-md transition-shadow">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-slate-900">AI Analysis</h2>
                <button
                    onClick={fetchAnalysis}
                    disabled={loading}
                    className="bg-slate-900 text-white hover:bg-slate-700 px-4 py-2 rounded-full font-medium text-sm transition-all disabled:opacity-50 shadow-sm"
                >
                    {loading ? "Analyzing..." : "Generate Analysis"}
                </button>
            </div>

            {analysis ? (
                <div className="flex-1 flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className={`p-6 rounded-2xl border flex flex-col items-center justify-center text-center ${getActionColor(analysis.final_action)}`}>
                        <div className="text-5xl font-bold tracking-tighter">{analysis.final_action}</div>
                        <div className={`mt-2 font-medium opacity-90`}>Confidence: {analysis.confidence}%</div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <div className="text-slate-500 text-xs uppercase tracking-wider font-semibold mb-1">Brief Rationale</div>
                            <div className="text-slate-800 text-lg leading-snug">{analysis.rationale_brief}</div>
                        </div>
                        <div>
                            <div className="text-slate-500 text-xs uppercase tracking-wider font-semibold mb-1">Technical Deep Dive</div>
                            <div className="text-slate-600 text-sm leading-relaxed">{analysis.rationale_technical}</div>
                        </div>

                        {renderChart()}

                        <div className="pt-4 border-t border-slate-100 flex justify-between items-center">
                            <span className="text-slate-500 text-sm">Risk Tier</span>
                            <span className="text-slate-700 font-medium bg-slate-100 px-3 py-1 rounded-lg border border-slate-200">{analysis.suggested_risk_tier}</span>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex-1 flex items-center justify-center text-slate-400 text-sm italic">
                    Click generate to start AI analysis
                </div>
            )}
        </div>
    );
}
