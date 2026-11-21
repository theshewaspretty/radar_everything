import { demoApi } from "./demo";

export type PeriodType = "weekly" | "monthly" | "yearly";

export type SourceInfo = {
  id: string;
  name: string;
  description: string;
  supports_periods: PeriodType[];
  supports_severity: boolean;
  enabled: boolean;
  last_collected_at: string | null;
};

export type PeriodInfo = {
  period_key: string;
  has_data: boolean;
  start: string | null;
  end: string | null;
};

export type TrendItem = {
  id: number;
  source: string;
  external_id: string;
  title: string;
  description: string;
  url: string;
  score: number;
  score_label: string;
  severity: string | null;
  language: string | null;
  owner: string | null;
  tags: string[];
  extra: Record<string, unknown>;
  period_type: PeriodType;
  period_key: string;
  rank: number;
  collected_at: string | null;
};

export type TrendsResponse = {
  source: string;
  period_type: PeriodType;
  period_key: string;
  count: number;
  items: TrendItem[];
};

export const IS_DEMO = import.meta.env.VITE_DEMO_MODE === "true";

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

const liveApi = {
  health: () => request<{ status: string; version: string }>("/api/health"),
  sources: () => request<{ sources: SourceInfo[] }>("/api/sources"),
  periods: (source: string, periodType: PeriodType) =>
    request<{ periods: PeriodInfo[] }>(`/api/periods/${source}/${periodType}`),
  trends: (params: {
    source: string;
    periodType: PeriodType;
    periodKey?: string;
    severity?: string;
    q?: string;
    limit?: number;
  }) => {
    const qs = new URLSearchParams({
      period_type: params.periodType,
      limit: String(params.limit ?? 30),
    });
    if (params.periodKey) qs.set("period_key", params.periodKey);
    if (params.severity) qs.set("severity", params.severity);
    if (params.q) qs.set("q", params.q);
    return request<TrendsResponse>(`/api/trends/${params.source}?${qs}`);
  },
  collect: (body: {
    source?: string;
    period_type?: PeriodType;
    period_key?: string;
    depth?: number;
  }) =>
    request<{ mode: string; status?: string; run?: { status: string; item_count: number } }>(
      "/api/collect?sync=true",
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),
  stats: () =>
    request<{
      total_items: number;
      by_source: Record<string, number>;
      last_run: { source: string; status: string; started_at: string | null } | null;
    }>("/api/stats"),
};

export const api = IS_DEMO ? demoApi : liveApi;
