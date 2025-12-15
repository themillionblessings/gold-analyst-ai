"use client";

import { useEffect, useState } from "react";

interface NewsItem {
    title: string;
    link: string;
    source?: string;
    date?: string;
}

export default function NewsFeed() {
    const [news, setNews] = useState<NewsItem[]>([]);

    useEffect(() => {
        fetch("http://localhost:8000/news")
            .then((res) => res.json())
            .then((data) => setNews(data))
            .catch((err) => console.error(err));
    }, []);

    return (
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
            <h2 className="text-xl font-semibold text-white mb-6">Market News</h2>
            <div className="space-y-4">
                {news.length > 0 ? (
                    news.slice(0, 3).map((item, idx) => (
                        <a
                            key={idx}
                            href={item.link}
                            target="_blank"
                            rel="noreferrer"
                            className="block p-4 rounded-xl bg-slate-900/50 border border-slate-700/30 hover:border-slate-500 transition-colors group"
                        >
                            <div className="text-xs text-emerald-400 font-medium mb-1 uppercase tracking-wide">{item.source || "News"}</div>
                            <div className="text-slate-200 font-medium group-hover:text-white transition-colors line-clamp-2">{item.title}</div>
                        </a>
                    ))
                ) : (
                    <div className="text-slate-500 text-sm">Loading news...</div>
                )}
            </div>
        </div>
    );
}
