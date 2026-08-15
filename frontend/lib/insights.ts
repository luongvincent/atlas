export interface Insight {
  slug: string;
  title: string;
  summary: string;
  date: string; // e.g. "Aug 15, 2026"
  readTime: string; // e.g. "4 min read"
  content: string[]; // one string per paragraph
}

export const INSIGHTS: Insight[] = [
  {
    slug: "reading-an-earnings-call-like-an-analyst",
    title: "Reading an earnings call like an analyst",
    summary:
      "Earnings calls are dense, scripted, and full of jargon. Here's what to actually listen for.",
    date: "Aug 15, 2026",
    readTime: "4 min read",
    content: [
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
      "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    ],
  },
  {
    slug: "why-average-daily-volume-matters",
    title: "Why average daily volume matters",
    summary:
      "A quick primer on what trading volume tells you - and what it doesn't.",
    date: "Aug 15, 2026",
    readTime: "3 min read",
    content: [
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
      "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.",
    ],
  },
];

export function getInsight(slug: string): Insight | undefined {
  return INSIGHTS.find((i) => i.slug === slug);
}