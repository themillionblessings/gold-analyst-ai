"use client";

import { useEffect, useState } from "react";
import PriceCard from "./components/PriceCard";
import AnalysisBlock from "./components/AnalysisBlock";
import NewsFeed from "./components/NewsFeed";
import MarketPrices from "./components/MarketPrices";
import GoldCalculator from "./components/GoldCalculator";
import DealAnalyzer from "./components/DealAnalyzer";
import MarketMoodGauge from "./components/MarketMoodGauge";
import { translations, Language } from "./translations";

// Define the full price data interface matching backend
interface PriceData {
  asset: string;
  price_oz_24k: number;
  daily_change_oz: number;
  percent_change: string;
  rates: Record<string, number>;
  usd: Record<string, number>;
  egypt: Record<string, number>;
  uae: Record<string, number>;
}

export default function Home() {
  const [priceData, setPriceData] = useState<PriceData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lang, setLang] = useState<Language>('en');

  useEffect(() => {
    async function fetchPrice() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${baseUrl}/price/GC=F`);
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`Status: ${res.status} ${res.statusText} - ${text.substring(0, 100)}`);
        }
        const json = await res.json();
        setPriceData(json);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch price data", err);
        setError(err instanceof Error ? err.message : "Unknown Error");
      }
    }
    fetchPrice();
    const interval = setInterval(fetchPrice, 60000);
    return () => clearInterval(interval);
  }, []);

  const t = translations[lang];

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans selection:bg-emerald-500/30" dir={lang === 'ar' ? 'rtl' : 'ltr'}>

      {/* Navbar */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-bold text-xl tracking-tight text-slate-900 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
            {t.title}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}
              className="text-sm font-medium text-slate-600 hover:text-emerald-600 transition-colors flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-full"
            >
              <span>{lang === 'en' ? '🇺🇸 EN' : '🇦🇪 AR'}</span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802" />
              </svg>
            </button>
            <div className="text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200 hidden md:block">
              {t.version}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12 space-y-8">

        {/* Hero Section */}
        <div className="space-y-2 text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
            {t.heroTitle}
          </h1>
          <p className="text-slate-500 text-lg">{t.heroSubtitle}</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 text-center">
            <p className="font-bold">{t.connectionError}</p>
            <p className="text-sm">{error}</p>
            <p className="text-xs mt-1 text-red-500">{t.errorDetail}</p>
          </div>
        )}

        {/* Market Mood Engine */}
        {/* Note: Components below need internal translation updates to fully support AR */}
        <div className="relative">
          <div className="absolute top-0 right-0 -mt-8 text-xs text-slate-400 font-bold uppercase tracking-widest">{t.marketMood}</div>
          <MarketMoodGauge />
        </div>

        {/* Top Data Row: Price Card + Calculator */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">{t.priceCard}</h3>
            <PriceCard data={priceData} />
          </div>
          <div className="md:col-span-1">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">{t.calculator}</h3>
            <GoldCalculator priceData={priceData} />
          </div>
        </div>

        {/* Market Data & Tools Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">{t.marketPrices}</h3>
            <MarketPrices priceData={priceData} />
          </div>
          <div className="md:col-span-1">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">{t.dealAnalyzer}</h3>
            <DealAnalyzer priceData={priceData} />
          </div>
        </div>

        {/* AI Analysis & News */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">{t.analysis}</h3>
            <AnalysisBlock />
          </div>
          <div className="md:col-span-1">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">{t.news}</h3>
            <NewsFeed />
          </div>
        </div>

      </main>
    </div>
  );
}
