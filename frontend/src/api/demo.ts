import type {
  PeriodInfo,
  PeriodType,
  SourceInfo,
  TrendItem,
  TrendsResponse,
} from "./client";

type RawItem = {
  external_id: string;
  title: string;
  description?: string;
  url: string;
  score: number;
  score_label?: string;
  severity?: string | null;
  language?: string | null;
  owner?: string | null;
  tags?: string[];
};

type Snapshot = {
  generated_at: string;
  sources: Array<Omit<SourceInfo, "last_collected_at"> & { last_collected_at?: string | null }>;
  bundles: Record<string, Record<PeriodType, RawItem[][]>>;
};

const STORAGE_KEY = "radar_everything_demo_overlay_v1";

let snapshotPromise: Promise<Snapshot> | null = null;
let overlay: Record<string, TrendItem[]> = loadOverlay();

function loadOverlay(): Record<string, TrendItem[]> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Record<string, TrendItem[]>) : {};
  } catch {
    return {};
  }
}

function saveOverlay() {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(overlay));
}

function overlayKey(source: string, periodType: PeriodType, periodKey: string) {
  return `${source}::${periodType}::${periodKey}`;
}

function mondayOf(d: Date): Date {
  const x = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const day = x.getUTCDay() || 7;
  if (day !== 1) x.setUTCDate(x.getUTCDate() - (day - 1));
  return x;
}

function isoWeekKey(d: Date): string {
  const tmp = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  tmp.setUTCDate(tmp.getUTCDate() + 4 - (tmp.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((tmp.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return `${tmp.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
}

function monthKey(d: Date): string {
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

export function listPeriodWindows(periodType: PeriodType, depth: number): PeriodInfo[] {
  const today = new Date();
  const out: PeriodInfo[] = [];
  for (let i = 0; i < depth; i++) {
    if (periodType === "weekly") {
      const start = mondayOf(today);
      start.setUTCDate(start.getUTCDate() - i * 7);
      const end = new Date(start);
      end.setUTCDate(start.getUTCDate() + 6);
      out.push({
        period_key: isoWeekKey(start),
        has_data: true,
        start: start.toISOString().slice(0, 10),
        end: end.toISOString().slice(0, 10),
      });
    } else if (periodType === "monthly") {
      const d = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth() - i, 1));
      const end = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0));
      out.push({
        period_key: monthKey(d),
        has_data: true,
        start: d.toISOString().slice(0, 10),
        end: end.toISOString().slice(0, 10),
      });
    } else {
      const y = today.getUTCFullYear() - i;
      out.push({
        period_key: String(y),
        has_data: true,
        start: `${y}-01-01`,
        end: `${y}-12-31`,
      });
    }
  }
  return out;
}

function periodOffset(periodType: PeriodType, periodKey: string): number {
  const windows = listPeriodWindows(periodType, 24);
  const idx = windows.findIndex((w) => w.period_key === periodKey);
  return idx < 0 ? 0 : idx;
}

async function loadSnapshot(): Promise<Snapshot> {
  if (!snapshotPromise) {
    snapshotPromise = fetch(`${import.meta.env.BASE_URL}demo-data/snapshot.json`).then(async (res) => {
      if (!res.ok) throw new Error("Demo snapshot load failed");
      return res.json() as Promise<Snapshot>;
    });
  }
  return snapshotPromise;
}

function toTrendItems(
  source: string,
  periodType: PeriodType,
  periodKey: string,
  raw: RawItem[],
): TrendItem[] {
  return raw.map((item, index) => ({
    id: index + 1,
    source,
    external_id: item.external_id,
    title: item.title,
    description: item.description || "",
    url: item.url,
    score: item.score,
    score_label: item.score_label || "score",
    severity: item.severity ?? null,
    language: item.language ?? null,
    owner: item.owner ?? null,
    tags: item.tags || [],
    extra: { demo: true },
    period_type: periodType,
    period_key: periodKey,
    rank: index + 1,
    collected_at: new Date().toISOString(),
  }));
}

function getBundleItems(
  snap: Snapshot,
  source: string,
  periodType: PeriodType,
  periodKey: string,
): TrendItem[] {
  const key = overlayKey(source, periodType, periodKey);
  if (overlay[key]?.length) return overlay[key];

  const series = snap.bundles[source]?.[periodType] || [];
  const offset = periodOffset(periodType, periodKey);
  const raw = series[Math.min(offset, Math.max(series.length - 1, 0))] || series[0] || [];
  return toTrendItems(source, periodType, periodKey, raw);
}

async function liveGithub(
  periodType: PeriodType,
  periodKey: string,
  queryExtra = "",
): Promise<TrendItem[]> {
  const windows = listPeriodWindows(periodType, 24);
  const win = windows.find((w) => w.period_key === periodKey) || windows[0];
  const start = win.start || "2026-01-01";
  const end = win.end || "2026-12-31";
  const baseQuery = queryExtra
    ? `${queryExtra} created:${start}..${end} stars:>1`
    : `created:${start}..${end} stars:>5`;
  const url =
    `https://api.github.com/search/repositories?q=${encodeURIComponent(baseQuery)}` +
    `&sort=stars&order=desc&per_page=20`;

  const res = await fetch(url, {
    headers: {
      Accept: "application/vnd.github+json",
      "User-Agent": "radar-everything-pages-demo",
    },
  });
  if (!res.ok) {
    throw new Error(`GitHub API ${res.status} (rate limit 가능). 샘플 데이터로 유지합니다.`);
  }
  const data = (await res.json()) as { items?: Array<Record<string, unknown>> };
  const items = data.items || [];
  return items.map((repo, index) => {
    const fullName = String(repo.full_name || "");
    return {
      id: index + 1,
      source: queryExtra.includes("mcp") ? "mcp" : "github",
      external_id: String(repo.id || fullName),
      title: fullName,
      description: String(repo.description || ""),
      url: String(repo.html_url || `https://github.com/${fullName}`),
      score: Number(repo.stargazers_count || 0),
      score_label: "stars",
      severity: null,
      language: (repo.language as string) || null,
      owner: (repo.owner as { login?: string } | undefined)?.login || null,
      tags: ((repo.topics as string[]) || []).slice(0, 8),
      extra: { demo_live: true },
      period_type: periodType,
      period_key: periodKey,
      rank: index + 1,
      collected_at: new Date().toISOString(),
    } satisfies TrendItem;
  });
}

export const demoApi = {
  isDemo: true as const,

  async health() {
    return { status: "ok", version: "demo", mode: "pages-demo" };
  },

  async sources() {
    const snap = await loadSnapshot();
    return {
      sources: snap.sources.map((s) => ({
        ...s,
        last_collected_at: s.last_collected_at ?? snap.generated_at,
      })) as SourceInfo[],
    };
  },

  async periods(source: string, periodType: PeriodType) {
    const snap = await loadSnapshot();
    const series = snap.bundles[source]?.[periodType] || [];
    const windows = listPeriodWindows(periodType, periodType === "yearly" ? 5 : 12);
    return {
      periods: windows.map((w, idx) => ({
        ...w,
        has_data: Boolean(overlay[overlayKey(source, periodType, w.period_key)]?.length || series[Math.min(idx, series.length - 1)]),
      })),
    };
  },

  async trends(params: {
    source: string;
    periodType: PeriodType;
    periodKey?: string;
    severity?: string;
    q?: string;
    limit?: number;
  }): Promise<TrendsResponse> {
    const snap = await loadSnapshot();
    const periodKey = params.periodKey || listPeriodWindows(params.periodType, 1)[0].period_key;
    let items = getBundleItems(snap, params.source, params.periodType, periodKey);

    if (params.severity) {
      items = items.filter((i) => (i.severity || "").toLowerCase() === params.severity!.toLowerCase());
    }
    if (params.q) {
      const q = params.q.toLowerCase();
      items = items.filter(
        (i) =>
          i.title.toLowerCase().includes(q) ||
          i.description.toLowerCase().includes(q) ||
          i.tags.some((t) => t.toLowerCase().includes(q)),
      );
    }
    items = items.slice(0, params.limit ?? 30);
    return {
      source: params.source,
      period_type: params.periodType,
      period_key: periodKey,
      count: items.length,
      items,
    };
  },

  async collect(body: {
    source?: string;
    period_type?: PeriodType;
    period_key?: string;
    depth?: number;
  }) {
    const source = body.source || "github";
    const periodType = body.period_type || "weekly";
    const periodKey = body.period_key || listPeriodWindows(periodType, 1)[0].period_key;

    try {
      if (source === "github") {
        const items = await liveGithub(periodType, periodKey);
        if (items.length) {
          overlay[overlayKey(source, periodType, periodKey)] = items;
          saveOverlay();
          return { mode: "demo-live", status: "ok", run: { status: "success", item_count: items.length } };
        }
      }
      if (source === "mcp") {
        const items = await liveGithub(periodType, periodKey, "topic:mcp-server");
        if (items.length) {
          overlay[overlayKey(source, periodType, periodKey)] = items;
          saveOverlay();
          return { mode: "demo-live", status: "ok", run: { status: "success", item_count: items.length } };
        }
      }
    } catch (err) {
      // Fall through to snapshot refresh
      console.warn(err);
    }

    // Snapshot refresh (vulnerability always; github/mcp fallback)
    const snap = await loadSnapshot();
    delete overlay[overlayKey(source, periodType, periodKey)];
    const refreshed = getBundleItems(snap, source, periodType, periodKey);
    overlay[overlayKey(source, periodType, periodKey)] = refreshed;
    saveOverlay();
    return {
      mode: "demo-snapshot",
      status: "ok",
      run: { status: "success", item_count: refreshed.length },
    };
  },

  async stats() {
    const snap = await loadSnapshot();
    const by_source: Record<string, number> = {};
    let total = 0;
    for (const [source, periods] of Object.entries(snap.bundles)) {
      let count = 0;
      for (const series of Object.values(periods)) {
        for (const bucket of series) count += bucket.length;
      }
      by_source[source] = count;
      total += count;
    }
    return {
      total_items: total,
      by_source,
      last_run: {
        source: "demo",
        status: "success",
        started_at: snap.generated_at,
      },
    };
  },
};
