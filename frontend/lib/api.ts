import type {
  ApiErrorBody,
  AskRequest,
  AskResponse,
  ChartRangeOption,
  ChartResponse,
  EtfHoldings,
  EtfsListResponse,
  ExplainResponse,
  OnboardingRequest,
  OnboardingResponse,
  SearchKind,
  SearchResponse,
  SentimentResult,
  SimilarItemsResponse,
  StrategyOverviewResponse,
  TickerStats,
  TickersListResponse,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit & { accessToken?: string } = {}): Promise<T> {
  const { accessToken, headers, ...rest } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      ...(rest.body ? { "Content-Type": "application/json" } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const body: ApiErrorBody = await response.json();
      message = body.detail ?? body.error ?? message;
    } catch {
      // response body wasn't JSON - fall back to statusText
    }
    throw new ApiError(response.status, message);
  }

  return (await response.json()) as T;
}

export function getTickers(): Promise<TickersListResponse> {
  return request<TickersListResponse>("/tickers");
}

export function searchStocks(query: string, kind: SearchKind, signal?: AbortSignal): Promise<SearchResponse> {
  return request<SearchResponse>(`/search?q=${encodeURIComponent(query)}&type=${kind}`, { signal });
}

export function requestExplanation(ticker: string, accessToken: string): Promise<{ ticker: string }> {
  return request<{ ticker: string }>("/explanation-requests", {
    method: "POST",
    body: JSON.stringify({ ticker }),
    accessToken,
  });
}

export function getExplanation(ticker: string, accessToken?: string): Promise<ExplainResponse> {
  return request<ExplainResponse>(`/explain/${encodeURIComponent(ticker)}`, { accessToken });
}

export function submitOnboarding(
  payload: OnboardingRequest,
  accessToken: string,
): Promise<OnboardingResponse> {
  return request<OnboardingResponse>("/onboarding", {
    method: "POST",
    body: JSON.stringify(payload),
    accessToken,
  });
}

export function getChart(ticker: string, range: ChartRangeOption): Promise<ChartResponse> {
  return request<ChartResponse>(
    `/chart/${encodeURIComponent(ticker)}?range=${encodeURIComponent(range)}`,
  );
}

export function getStats(ticker: string): Promise<TickerStats> {
  return request<TickerStats>(`/stats/${encodeURIComponent(ticker)}`);
}

export function getEtfs(): Promise<EtfsListResponse> {
  return request<EtfsListResponse>("/etfs");
}

export function getEtfsCa(): Promise<EtfsListResponse> {
  return request<EtfsListResponse>("/etfs/ca");
}

export function getEtfHoldings(ticker: string): Promise<EtfHoldings> {
  return request<EtfHoldings>(`/etfs/${encodeURIComponent(ticker)}/holdings`);
}

export function getStrategyOverview(accessToken: string): Promise<StrategyOverviewResponse> {
  return request<StrategyOverviewResponse>("/strategy-overview", { accessToken });
}

export function getSimilarItems(ticker: string): Promise<SimilarItemsResponse> {
  return request<SimilarItemsResponse>(`/similar/${encodeURIComponent(ticker)}`);
}

export async function getOnboarding(
  accessToken: string,
): Promise<OnboardingResponse | null> {
  try {
    return await request<OnboardingResponse>("/onboarding", {
      accessToken,
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }

    throw err;
  }
}
export function getSentiment(ticker: string): Promise<SentimentResult> {
  return request<SentimentResult>(`/sentiment/${encodeURIComponent(ticker)}`);
}

export function askQuestion(ticker: string, payload: AskRequest, accessToken: string): Promise<AskResponse> {
  return request<AskResponse>(`/ask/${encodeURIComponent(ticker)}`, {
    method: "POST",
    body: JSON.stringify(payload),
    accessToken,
  });
}
