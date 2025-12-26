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
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        fetch(`${baseUrl}/news`)
            .then((res) => res.json())
            .then((data) => setNews(data))
            .catch((err) => console.error(err));
    }, []);

    return (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Market News</h2>
            <div className="space-y-4">
                {news.length > 0 ? (
                    news.slice(0, 3).map((item, idx) => (
                        <a
                            key={idx}
                            href={item.link}
                            target="_blank"
                            rel="noreferrer"
                            className="block p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-slate-300 transition-colors group"
                        >
                            <div className="text-xs text-blue-600 font-medium mb-1 uppercase tracking-wide">{item.source || "News"}</div>
                            <div className="text-slate-800 font-medium group-hover:text-blue-700 transition-colors line-clamp-2">{item.title}</div>
                        </a>
                    ))
                ) : (
                    <div className="text-slate-400 text-sm">Loading news...</div>
                )}
            </div>
        </div>
    );
}
