"use client";

import { useEffect, useState } from "react";
import PriceCard from "./components/PriceCard";
import AnalysisBlock from "./components/AnalysisBlock";
import NewsFeed from "./components/NewsFeed";
import MarketPrices from "./components/MarketPrices";
import GoldCalculator from "./components/GoldCalculator";
import DealAnalyzer from "./components/DealAnalyzer";

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

  useEffect(() => {
    async function fetchPrice() {
      try {
        const res = await fetch("/api/proxy/price/GC=F");
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

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans selection:bg-emerald-500/30">

      {/* Navbar */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-bold text-xl tracking-tight text-slate-900 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
            GOLD ANALYST AI
          </div>
          <div className="text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
            v2.1 Light
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12 space-y-8">

        {/* Hero Section */}
        <div className="space-y-2 text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
            Smart Market Intelligence
          </h1>
          <p className="text-slate-500 text-lg">Real-time gold tracking powered by Gemini 2.5 Flash.</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 text-center">
            <p className="font-bold">Connection Error</p>
            <p className="text-sm">{error}</p>
            <p className="text-xs mt-1 text-red-500">Check Render Logs: Frontend or Backend may be down.</p>
          </div>
        )}

        {/* Top Data Row: Price Card + Calculator */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            {/* Pass data to PriceCard (requires refactor of PriceCard to accept props) */}
            <PriceCard data={priceData} />
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
