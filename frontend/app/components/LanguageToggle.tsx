"use client";

import { useLanguage } from "../context/LanguageContext";
import { Globe } from "lucide-react";

export default function LanguageToggle() {
    const { language, setLanguage } = useLanguage();

    const toggleLanguage = () => {
        setLanguage(language === 'en' ? 'ar' : 'en');
    };

    return (
        <button
            onClick={toggleLanguage}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white hover:bg-slate-50 border border-emerald-500/30 shadow-sm transition-all text-slate-700 font-medium text-sm active:scale-95"
            aria-label="Toggle Language"
        >
            <Globe className="w-4 h-4" />
            <span className="font-sans">
                {language === 'en' ? 'Arabic' : 'English'}
            </span>
            <span className="font-serif opacity-50">
                {language === 'en' ? 'عربي' : 'En'}
            </span>
        </button>
    );
}
