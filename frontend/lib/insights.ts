import type { InvestingExperience } from "./types";

export interface Insight {
  slug: string;
  title: string;
  summary: string;
  date: string; // e.g. "Aug 15, 2026"
  readTime: string; // e.g. "4 min read"
  content: string[]; // one string per paragraph
  // Which investing_experience levels this is most useful for - drives
  // the "Recommended for you" widget on the onboarding results screen.
  // Not a hard gate: every article is still reachable by anyone from the
  // /learn index regardless of this tagging, same "adapt, never gate"
  // principle the risk-profile quiz itself follows.
  relevantExperience: InvestingExperience[];
}

export const INSIGHTS: Insight[] = [
  {
    slug: "why-average-daily-volume-matters",
    title: "Why average daily volume matters",
    summary:
      "It's why these particular tickers and ETFs are on Atlas at all. Here's what it means, and what it doesn't.",
    date: "Aug 18, 2026",
    readTime: "3 min read",
    relevantExperience: ["none", "beginner"],
    content: [
      "Average daily volume is just a count: on a normal day, how many shares of a stock (or units of an ETF) actually change hands. Atlas shows it on every ticker and ETF card, and it's also how the roster itself was chosen - the 15 stocks and the 15-plus-15 US/Canadian ETFs on this site are the most actively traded ones, not a hand-picked \"best of\" list.",
      "Why rank by volume instead of, say, company size or popularity on social media? Volume is a decent proxy for two things that actually matter practically: enough people care about this to be trading it every day, and it's liquid - meaning you could buy or sell a normal amount of it without the price jumping around just because of your own order. A stock that trades a few hundred shares a day can swing 10% on a single trade; one trading tens of millions a day generally can't.",
      "What volume does not tell you is whether something is a good investment, fairly priced, or safe. A stock can be heavily traded and still be a bad idea, or be quiet and steady and a perfectly fine one. High volume often just means high attention - sometimes that's genuine investor interest, sometimes it's short-term speculation. Treat it as \"this is easy to buy and sell, and a lot of people are watching it,\" not as a stamp of quality.",
    ],
  },
  {
    slug: "how-to-read-the-price-chart",
    title: "How to read the price chart",
    summary:
      "The range tabs, the color, and what a wiggly line can and can't tell you about a stock.",
    date: "Aug 18, 2026",
    readTime: "3 min read",
    relevantExperience: ["none", "beginner"],
    content: [
      "Every ticker and ETF page has a price chart with range tabs across the top - 1D, 5D, 1M, 6M, YTD, 1Y, 5Y, and ALL. Switching ranges doesn't just zoom the same data in and out; it asks for a different slice of history, so a 1-day chart shows price movement through the trading day while a 5-year chart shows one point per week rather than every single trade - otherwise five years of minute-by-minute data would be unreadable (and slow to load).",
      "The line is colored green when the price is up over the period you're looking at, and red when it's down - but the color is never the only signal. The exact dollar and percent change is always printed as text right above the chart, so you're never guessing at a shade of green. Hover (or tap) anywhere on the line to see the exact price and date at that point.",
      "The one thing a price chart genuinely can't tell you is what happens next. A stock that's up 20% over the past year could keep climbing or could give it all back tomorrow - past price movement describes what already happened, it doesn't predict what's coming. It's most useful for context (\"has this been a calm or a volatile year?\") rather than as a forecast.",
    ],
  },
  {
    slug: "reading-an-earnings-call-like-an-analyst",
    title: "Reading an earnings call like an analyst",
    summary:
      "Earnings calls are dense, scripted, and full of hedged language. Here's what the four sections on Atlas are actually pulling out for you.",
    date: "Aug 18, 2026",
    readTime: "4 min read",
    relevantExperience: ["none", "beginner", "intermediate"],
    content: [
      "A real earnings call transcript can run 40-plus pages: a scripted opening from management, then a Q&A with analysts who ask pointed, sometimes skeptical questions. Reading the whole thing takes real effort, most of it not that informative - which is the whole reason Atlas exists. Every ticker's explanation is broken into four sections that map to what an experienced reader is actually looking for.",
      "\"What happened\" is the headline numbers - revenue, profit, growth - translated out of finance-speak. \"What management actually said\" covers guidance and tone, and this is the section worth reading most carefully: management rarely lies outright, but they hedge constantly. Phrases like \"we expect\" or \"we remain optimistic\" are doing real work - they're weaker commitments than \"we will\" or \"we are confident,\" and Atlas flags this hedging explicitly rather than letting it slide by as confident-sounding language.",
      "\"What analysts pushed back on\" comes from the Q&A, where the actual scrutiny happens - management's opening remarks are written in advance and polished; analyst questions are live and often adversarial. This is frequently the most honest part of a call. \"Why it matters\" is the plain-language takeaway - what this quarter's results actually mean for the business going forward, without jargon.",
      "Every claim in these four sections links back to a citation - who said it, and whether it came from the prepared remarks or the Q&A - so nothing is just asserted. If a claim seems surprising, the citation is there so you can trace it back to what was actually said, rather than having to trust a summary on faith.",
    ],
  },
  {
    slug: "making-sense-of-valuation-stats",
    title: "Making sense of the valuation stats",
    summary:
      "P/E, P/B, PEG, and dividend yield, in plain language - plus the honest limits of any single ratio.",
    date: "Aug 18, 2026",
    readTime: "4 min read",
    relevantExperience: ["beginner", "intermediate"],
    content: [
      "The \"Valuation & Profitability\" numbers on every stock and ETF page answer one basic question: how much are you paying for what you're actually getting? P/E (price-to-earnings) compares the price to the company's yearly profit - a P/E of 20 means paying $20 for every $1 the company earns in a year. Roughly 15-25 is a common range for an established company; below that can mean undervalued (or the market has real concerns), and well above it usually means investors are betting on fast future growth rather than paying for today's profit.",
      "P/B (price-to-book) compares the price to what the company would theoretically be worth if it sold everything and paid off its debts. PEG takes the P/E and adjusts it for expected growth, so a fast-growing company with a high P/E can still have a PEG near 1 - \"fair value given how fast it's growing.\" Dividend yield is simply the percentage of the share price paid back to you each year in cash; mature, stable companies (banks, utilities) tend to pay more, while growth companies often pay nothing at all and reinvest instead.",
      "The honest caveat: none of these numbers mean much in isolation. A P/E of 40 is unremarkable for a fast-growing tech company and alarming for a slow-growing utility - the \"right\" range depends heavily on the industry and the company's own history, not a single universal cutoff. Use them to compare similar companies to each other, or a company to its own past, rather than treating any one number as a verdict on its own. Every stat on Atlas has a small \"ⓘ\" next to it with this same context, so you don't have to remember the specifics.",
    ],
  },
  {
    slug: "sharpe-sortino-beta-alpha-explained",
    title: "What Sharpe, Sortino, Beta, and Alpha actually tell you",
    summary:
      "Four risk numbers that sound intimidating and mean something fairly simple once you break them down.",
    date: "Aug 18, 2026",
    readTime: "4 min read",
    relevantExperience: ["intermediate", "experienced"],
    content: [
      "These four numbers, shown together under \"Risk & Performance,\" are all trying to answer some version of the same question: given how much this investment moves around, was it actually worth holding? Beta is the simplest starting point - it measures how much a stock swings compared to the overall market over the past year. A beta of 1.0 means it roughly tracks the market; above 1 means bigger swings in both directions, below 1 means smaller, steadier moves.",
      "Alpha builds on beta: it's the extra return (or shortfall) an investment delivered beyond what its beta would predict, over the past year. Positive alpha means it beat what its risk level alone would suggest; negative means it fell short. It's usually a small number - a few percentage points either way - so treat a large alpha as notable rather than expected.",
      "Sharpe and Sortino both measure return-per-unit-of-risk, just with slightly different definitions of \"risk.\" Sharpe uses all price volatility, up and down alike; Sortino only counts the downside, so it doesn't penalize an investment for volatility that happened to work in your favor. For both, above 1 is generally considered good, above 2 is very good, and a negative number means the investment didn't even beat a safe, boring alternative like a Treasury bond over that period.",
      "All four of these are calculated from the trailing 12 months, recalculated fresh each time you load the page - they describe recent history, not a guarantee about what comes next. A stock with a great Sharpe ratio last year can have a rough one this year. They're most useful for comparing two options against each other right now, not as a permanent score.",
    ],
  },
  {
    slug: "understanding-an-etfs-holdings-breakdown",
    title: "Understanding an ETF's holdings breakdown",
    summary:
      "What the donut chart, the top-holdings list, and that \"Other\" slice on every ETF page are actually showing.",
    date: "Aug 18, 2026",
    readTime: "3 min read",
    relevantExperience: ["none", "beginner", "intermediate", "experienced"],
    content: [
      "An ETF is a basket of many holdings wrapped into one ticker you can buy - the whole point of the holdings breakdown is to show you what's actually inside the basket. The bar list ranks the largest individual holdings by exact weight; the donut chart above it gives the same information as a quick visual - the biggest few names as distinct colored slices, sized by how much of the fund they make up.",
      "The \"Other\" slice is important to read correctly, and it doesn't always mean the same thing. For a well-covered fund tracking hundreds of companies, \"Other\" is real - it's every holding ranked below what's individually listed, genuinely part of the fund, just not itemized one by one. For smaller or less-covered funds, \"Other\" can instead mean the data source simply doesn't disclose more detail for that particular fund - in that case it's less \"here's everything else\" and more \"unknown to us.\" Hovering the Other slice (or reading the note beneath the chart) tells you which situation applies.",
      "The sector breakdown answers a related but different question: not which individual companies, but which parts of the economy the fund is exposed to - technology, financials, energy, and so on. A fund concentrated 40% in one sector behaves very differently from one spread evenly across ten - worth checking if you're trying to avoid overlapping bets across multiple things you own.",
    ],
  },
  {
    slug: "what-your-risk-profile-changes",
    title: "What your risk profile actually changes",
    summary:
      "The 5-question quiz under Preferences doesn't gate anything or give advice - here's exactly what it does do.",
    date: "Aug 18, 2026",
    readTime: "2 min read",
    relevantExperience: ["none", "beginner"],
    content: [
      "The risk profile quiz asks five short questions - investing experience, time horizon, comfort with risk, portfolio size, and your main goal - and combines them into one label: conservative, moderate, or aggressive. It's intentionally short, and none of the questions are trick questions; answer honestly rather than trying to game a particular result.",
      "What it actually changes is narrow and specific. If your answers mark you as newer to investing, explanations you read afterward get a short glossary of finance terms used in that specific write-up, so you're not left guessing what \"guidance\" or \"gross margin\" means. Your risk profile also adds one tailored closing sentence to the \"why it matters\" section, angled toward what someone with your risk comfort would likely want to weigh most.",
      "What it deliberately does not do: it doesn't hide any ticker or ETF from you, doesn't restrict what you can read, and doesn't generate investment advice or a recommendation to buy or sell anything. The underlying explanation - the facts, the citations, the numbers - is exactly the same for everyone; the quiz only adjusts how much hand-holding and framing gets layered on top of it.",
    ],
  },
];

export function getInsight(slug: string): Insight | undefined {
  return INSIGHTS.find((i) => i.slug === slug);
}

// Ordinal distance between experience levels, for ranking articles that
// don't exactly match the reader's level - a "beginner" article is a
// closer fallback for a "none" reader than a "sharpe/sortino" one tagged
// only for "experienced". Simple rule-based scoring, not a learned model -
// see CLAUDE.md for why collaborative filtering was ruled out at this
// project's actual user scale.
const EXPERIENCE_ORDER: InvestingExperience[] = ["none", "beginner", "intermediate", "experienced"];

function experienceDistance(a: InvestingExperience, b: InvestingExperience): number {
  return Math.abs(EXPERIENCE_ORDER.indexOf(a) - EXPERIENCE_ORDER.indexOf(b));
}

/**
 * Ranks articles by relevance to a reader's investing experience level.
 * Never excludes anything - every article is still reachable from /learn
 * regardless of this ranking, same "adapt tone/depth, never gate content"
 * principle as the rest of the risk-profile-driven personalization.
 */
export function getRecommendedInsights(
  experience: InvestingExperience,
  limit = 3,
): Insight[] {
  return [...INSIGHTS]
    .map((insight) => ({
      insight,
      distance: Math.min(...insight.relevantExperience.map((e) => experienceDistance(experience, e))),
    }))
    .sort((a, b) => a.distance - b.distance)
    .slice(0, limit)
    .map(({ insight }) => insight);
}
