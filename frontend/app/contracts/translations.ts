export type Language = 'en' | 'ar';

export const translations = {
    en: {
        appTitle: "GOLD ANALYST AI",
        version: "v2.1 Light",
        heroTitle: "Smart Market Intelligence",
        heroSubtitle: "Real-time gold tracking powered by AI.",
        connectionError: "Connection Error",
        connectionErrorHelp: "Check Render Logs: Frontend or Backend may be down.",
        marketMood: "Market Mood",
        realTimeAnalysis: "Real-Time Analysis",
        bearish: "Bearish",
        neutral: "Neutral",
        bullish: "Bullish",
        keyFactors: "Key Sentiment Factors",
        analyzing: "Gauging Market Sentiment...",
    },
    ar: {
        appTitle: "محلل الذهب الذكي",
        version: "إصدار 2.1 لايت",
        heroTitle: "ذكاء السوق المتقدم",
        heroSubtitle: "تتبع أسعار الذهب لحظياً بدعم من الذكاء الاصطناعي.",
        connectionError: "خطأ في الاتصال",
        connectionErrorHelp: "تحقق من سجلات الخادم: قد تكون الخدمة متوقفة.",
        marketMood: "مزاج السوق",
        realTimeAnalysis: "تحليل فوري",
        bearish: "هبوطي",
        neutral: "محايد",
        bullish: "صعودي",
        keyFactors: "عوامل التأثير الرئيسية",
        analyzing: "جاري تحليل مشاعر السوق...",
    }
};

export type TranslationKey = keyof typeof translations.en;
