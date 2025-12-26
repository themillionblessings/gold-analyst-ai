"use client";

import { useEffect, useState } from "react";

interface MarketMood {
    sentiment_score: number;
    mood_label: string;
    key_factors: string[];
    error?: boolean;
}

export default function MarketMoodGauge() {
    const [mood, setMood] = useState<MarketMood | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMood = async () => {
            try {
                const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${baseUrl}/market-mood`);
                const data = await res.json();
                setMood(data);
            } catch (err) {
                console.error("Failed to fetch market mood", err);
            } finally {
                setLoading(false);
            }
        };
        fetchMood();
    }, []);

    if (loading) {
        return (
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm animate-pulse h-[200px] flex items-center justify-center">
                <div className="text-slate-400">Analyzing Market Sentiment...</div>
            </div>
        );
    }

    if (!mood) return null;

    const getScoreColor = (score: number) => {
        if (score >= 70) return "bg-emerald-500";
        if (score >= 40) return "bg-amber-500";
        return "bg-rose-500";
    };

    const getScoreWidth = (score: number) => `${score}%`;

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-all overflow-hidden relative">
            {/* Background Glow */}
            <div className={`absolute -top-24 -right-24 w-48 h-48 blur-3xl opacity-10 rounded-full ${getScoreColor(mood.sentiment_score)}`}></div>

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 relative z-10">
                <div className="flex-1 space-y-4">
                    <div className="flex items-center gap-3">
                        <h2 className="text-xl font-semibold text-slate-900">Market Mood</h2>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${mood.sentiment_score >= 70 ? 'bg-emerald-100 text-emerald-700' : mood.sentiment_score >= 40 ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'}`}>
                            {mood.mood_label}
                        </span>
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between text-sm font-medium">
                            <span className="text-slate-500 italic">Sentiment Score</span>
                            <span className="text-slate-900 font-bold">{mood.sentiment_score}/100</span>
                        </div>
                        <div className="h-4 bg-slate-100 rounded-full overflow-hidden shadow-inner p-0.5">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ease-out shadow-sm ${getScoreColor(mood.sentiment_score)}`}
                                style={{ width: getScoreWidth(mood.sentiment_score) }}
                            ></div>
                        </div>
                        <div className="flex justify-between text-[10px] uppercase tracking-widest font-bold text-slate-400 px-1">
                            <span>Bearish</span>
                            <span>Neutral</span>
                            <span>Bullish</span>
                        </div>
                    </div>
                </div>

                <div className="flex-1">
                    <div className="text-slate-500 text-xs uppercase tracking-wider font-semibold mb-3">Key Sentiment Factors</div>
                    <div className="flex flex-wrap gap-2">
                        {mood.key_factors.map((factor, idx) => (
                            <span
                                key={idx}
                                className="bg-slate-50 border border-slate-100 text-slate-700 px-3 py-1.5 rounded-xl text-sm font-medium hover:border-slate-300 transition-colors shadow-sm"
                            >
                                {factor}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
