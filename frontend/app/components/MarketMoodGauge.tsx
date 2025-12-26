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
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm animate-pulse h-[250px] flex items-center justify-center">
                <div className="text-slate-400">Gauging Market Sentiment...</div>
            </div>
        );
    }

    if (!mood) return null;

    // Gauge Calculation
    // Score 0-100 mapped to rotation -90deg to 90deg
    const rotation = (mood.sentiment_score / 100) * 180 - 90;

    const getMoodColor = (score: number) => {
        if (score >= 70) return "#10b981"; // emerald-500
        if (score >= 40) return "#f59e0b"; // amber-500
        return "#ef4444"; // rose-500
    };

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-all relative overflow-hidden">
            <div className="flex flex-col items-center">
                <div className="w-full flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold text-slate-900">Market Mood</h2>
                        <p className="text-xs text-slate-400 uppercase tracking-widest font-bold">Real-Time Analysis</p>
                    </div>
                    <span className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest shadow-sm ${mood.sentiment_score >= 70 ? 'bg-emerald-500 text-white' :
                            mood.sentiment_score >= 40 ? 'bg-amber-500 text-white' :
                                'bg-rose-500 text-white'
                        }`}>
                        {mood.mood_label}
                    </span>
                </div>

                {/* SVG Gauge Implementation */}
                <div className="relative w-64 h-32 mb-8 mt-4">
                    {/* Background Track */}
                    <svg viewBox="0 0 100 50" className="w-full h-full">
                        <path
                            d="M 10 50 A 40 40 0 0 1 90 50"
                            fill="none"
                            stroke="#f1f5f9"
                            strokeWidth="10"
                            strokeLinecap="round"
                        />
                        <path
                            d="M 10 50 A 40 40 0 0 1 90 50"
                            fill="none"
                            stroke="url(#gauge-gradient)"
                            strokeWidth="10"
                            strokeLinecap="round"
                            strokeDasharray="125.6"
                            strokeDashoffset={125.6 - (125.6 * (mood.sentiment_score / 100))}
                            className="transition-all duration-1000 ease-out"
                        />
                        <defs>
                            <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#ef4444" />
                                <stop offset="50%" stopColor="#f59e0b" />
                                <stop offset="100%" stopColor="#10b981" />
                            </linearGradient>
                        </defs>
                    </svg>

                    {/* Needle */}
                    <div
                        className="absolute bottom-0 left-1/2 w-1 h-32 origin-bottom transition-transform duration-1000 ease-out"
                        style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
                    >
                        <div className="w-1 h-20 bg-slate-900 rounded-full shadow-lg"></div>
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-slate-900 rounded-full border-2 border-white"></div>
                    </div>

                    {/* Score Center */}
                    <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-center text-3xl font-black text-slate-800">
                        {mood.sentiment_score}<span className="text-sm text-slate-400 font-medium">/100</span>
                    </div>
                </div>

                {/* Legend */}
                <div className="w-full flex justify-between text-[10px] font-black uppercase tracking-tighter text-slate-400 px-8 mb-8">
                    <span className="text-rose-400">Bearish</span>
                    <span>Neutral</span>
                    <span className="text-emerald-400">Bullish</span>
                </div>

                {/* Key Factors as Bullets */}
                <div className="w-full bg-slate-50 rounded-2xl p-6 border border-slate-100">
                    <h3 className="text-xs uppercase tracking-widest font-black text-slate-500 mb-4 flex items-center gap-2">
                        <span className="w-4 h-0.5 bg-slate-400"></span>
                        Key Sentiment Factors
                    </h3>
                    <ul className="space-y-3">
                        {mood.key_factors.map((factor, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                                <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${mood.sentiment_score >= 70 ? 'bg-emerald-400' :
                                        mood.sentiment_score >= 40 ? 'bg-amber-400' :
                                            'bg-rose-400'
                                    }`}></div>
                                <span className="text-sm font-medium text-slate-600 leading-relaxed italic">
                                    {factor}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}
