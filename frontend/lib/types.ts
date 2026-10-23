export interface TickerInfo {
  ticker: string;
  company_name: string;
  avg_daily_volume: number;
  exchange: string;
  latest_quarter: string | null;
  latest_call_date: string | null;
}

export interface TickersListResponse {
  tickers: TickerInfo[];
}

export type SearchKind = "stock" | "etf";

export interface SearchResult {
  ticker: string;
  company_name: string;
  exchange: string;
  kind: SearchKind;
  supported: boolean;
  leveraged: boolean;
}

export interface SearchResponse {
  results: SearchResult[];
  other_matches: SearchResult[];
}

export interface Citation {
  claim: string;
  speaker: string;
  section: "prepared_remarks" | "qa";
}

export interface ExplanationSections {
  what_happened: string;
  what_management_said: string;
  what_analysts_pushed_back_on: string;
  why_it_matters: string;
}

export interface GlossaryEntry {
  term: string;
  definition: string;
}

export interface ExplainResponse {
  ticker: string;
  company_name: string;
  quarter: string;
  sections: ExplanationSections;
  citations: Citation[];
  cached: boolean;
  generated_at: string | null;
  glossary: GlossaryEntry[];
  definitions: GlossaryEntry[];
}

export type InvestingExperience = "none" | "beginner" | "intermediate" | "experienced";
export type TimeHorizon = "short_term" | "medium_term" | "long_term";
export type PortfolioSizeRange = "under_1k" | "1k_10k" | "10k_100k" | "100k_1m" | "over_1m";
export type Goal = "preserve_capital" | "income" | "growth" | "speculation";
export type RiskProfileLabel = "conservative" | "moderate" | "aggressive";

export interface OnboardingRequest {
  investing_experience: InvestingExperience;
  time_horizon: TimeHorizon;
  risk_comfort: number;
  portfolio_size_range: PortfolioSizeRange;
  goals: Goal;
}

export interface OnboardingResponse extends OnboardingRequest {
  risk_profile: RiskProfileLabel;
}

export interface ApiErrorBody {
  detail?: string;
  error?: string;
}

export type ChartRangeOption = "1D" | "5D" | "1M" | "6M" | "YTD" | "1Y" | "5Y" | "ALL";

export interface ChartPoint {
  timestamp: string;
  close: number;
}

export interface ChartResponse {
  ticker: string;
  range: string;
  interval: string;
  points: ChartPoint[];
}

export interface TickerStats {
  ticker: string;
  pe_ratio: number | null;
  pb_ratio: number | null;
  peg_ratio: number | null;
  dividend_yield: number | null;
  beta: number | null;
  alpha: number | null;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
}

export interface EtfInfo {
  ticker: string;
  name: string;
  avg_daily_volume: number;
  exchange: string;
  category: string;
}

export interface EtfsListResponse {
  etfs: EtfInfo[];
}

export interface HoldingEntry {
  ticker: string;
  name: string;
  weight_percent: number;
}

export interface SectorWeight {
  sector: string;
  weight_percent: number;
}

export interface EtfHoldings {
  ticker: string;
  top_holdings: HoldingEntry[];
  sector_weightings: SectorWeight[];
}
