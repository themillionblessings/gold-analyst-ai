import PriceCard from "./components/PriceCard";
import AnalysisBlock from "./components/AnalysisBlock";
import NewsFeed from "./components/NewsFeed";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500/30">

      {/* Navbar */}
      <nav className="border-b border-slate-800/60 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-bold text-xl tracking-tight text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.5)]"></span>
            GOLD ANALYST AI
          </div>
          <div className="text-xs font-medium text-slate-500 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">
            v2.0 Beta
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12 space-y-8">

        {/* Hero Section */}
        <div className="space-y-2 text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-400">
            Smart Market Intelligence
          </h1>
          <p className="text-slate-400 text-lg">Real-time gold tracking powered by Gemini 2.5 Flash.</p>
        </div>

        {/* Top Data Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <PriceCard />
          </div>
          <div className="md:col-span-1">
            <NewsFeed />
          </div>
        </div>

        {/* Main Analysis Block */}
        <div className="h-full">
          <AnalysisBlock />
        </div>

      </main>
    </div>
  );
}
