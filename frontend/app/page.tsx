"use client";

import { useEffect, useState } from "react";
import PriceCard from "./components/PriceCard";
import AnalysisBlock from "./components/AnalysisBlock";
import NewsFeed from "./components/NewsFeed";
import MarketPrices from "./components/MarketPrices";
import GoldCalculator from "./components/GoldCalculator";
import DealAnalyzer from "./components/DealAnalyzer";
import MarketMoodGauge from "./components/MarketMoodGauge";

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

export interface ValidatedGoldResponse {
  final_price: number;
  source: string;
  anomaly_detected: boolean;
  system_note?: string;
}

import { useLanguage } from "./context/LanguageContext";
import LanguageToggle from "./components/LanguageToggle";

export default function Home() {
  const [priceData, setPriceData] = useState<PriceData | null>(null);
  const [validatedData, setValidatedData] = useState<ValidatedGoldResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { t, dir } = useLanguage();

  useEffect(() => {
    async function fetchPrice() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Fetch legacy data for supplementary UI
        const res = await fetch(`${baseUrl}/price/GC=F`);
        if (!res.ok) throw new Error(`Status: ${res.status}`);
        setPriceData(await res.json());

        // Fetch validated core price from LangGraph Supervisor
        const valRes = await fetch(`${baseUrl}/api/v1/gold/validated-price`);
        if (valRes.ok) setValidatedData(await valRes.json());

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

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans selection:bg-emerald-500/30" dir={dir}>

      {/* Navbar */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-bold text-xl tracking-tight text-slate-900 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
            {t('appTitle')}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200 hidden sm:block">
              {t('version')}
            </div>
            <LanguageToggle />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12 space-y-8">

        {/* Hero Section */}
        <div className="space-y-2 text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
            {t('heroTitle')}
          </h1>
          <p className="text-slate-500 text-lg">{t('heroSubtitle')}</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 text-center">
            <p className="font-bold">{t('connectionError')}</p>
            <p className="text-sm">{error}</p>
            <p className="text-xs mt-1 text-red-500">{t('connectionErrorHelp')}</p>
          </div>
        )}

        {/* Market Mood Engine */}
        <MarketMoodGauge />

        {/* Top Data Row: Price Card + Calculator */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            {/* Pass data to PriceCard (requires refactor of PriceCard to accept props) */}
            <PriceCard data={priceData} validatedData={validatedData} />
          </div>
          <div className="md:col-span-1">
            <GoldCalculator priceData={priceData} />
          </div>
        </div>

        {/* Market Data & Tools Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <MarketPrices priceData={priceData} />
          </div>
          <div className="md:col-span-1">
            <DealAnalyzer priceData={priceData} />
          </div>
        </div>

        {/* AI Analysis & News */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <AnalysisBlock />
          </div>
          <div className="md:col-span-1">
            <NewsFeed />
          </div>
        </div>

      </main>
    </div>
  );
}
