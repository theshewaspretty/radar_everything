import { useDeferredValue, useEffect, useMemo, useState } from "react";
import {
  api,
  type PeriodInfo,
  type PeriodType,
  type SourceInfo,
  type TrendItem,
} from "./api/client";
import { RadarStage } from "./components/RadarStage";
import { TrendList } from "./components/TrendList";

const PERIOD_LABELS: Record<PeriodType, string> = {
  weekly: "주간",
  monthly: "월간",
  yearly: "연간",
};

const SEVERITIES = ["", "critical", "high", "medium", "low"] as const;

export default function App() {
  const [sources, setSources] = useState<SourceInfo[]>([]);
  const [source, setSource] = useState("github");
  const [periodType, setPeriodType] = useState<PeriodType>("weekly");
  const [periods, setPeriods] = useState<PeriodInfo[]>([]);
  const [periodKey, setPeriodKey] = useState<string | undefined>();
  const [severity, setSeverity] = useState("");
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [items, setItems] = useState<TrendItem[]>([]);
  const [activePeriodKey, setActivePeriodKey] = useState("");
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statsText, setStatsText] = useState("");

  const activeSource = useMemo(
    () => sources.find((s) => s.id === source),
    [sources, source],
  );

  useEffect(() => {
    api
      .sources()
      .then((res) => {
        setSources(res.sources);
        if (res.sources.length && !res.sources.some((s) => s.id === source)) {
          setSource(res.sources[0].id);
        }
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    let cancelled = false;
    api
      .periods(source, periodType)
      .then((res) => {
        if (cancelled) return;
        setPeriods(res.periods);
        const preferred =
          res.periods.find((p) => p.has_data)?.period_key ?? res.periods[0]?.period_key;
        setPeriodKey(preferred);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [source, periodType]);

  useEffect(() => {
    if (!periodKey) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .trends({
        source,
        periodType,
        periodKey,
        severity: severity || undefined,
        q: deferredQuery || undefined,
      })
      .then((res) => {
        if (cancelled) return;
        setItems(res.items);
        setActivePeriodKey(res.period_key);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [source, periodType, periodKey, severity, deferredQuery]);

  useEffect(() => {
    api
      .stats()
      .then((s) => {
        const parts = Object.entries(s.by_source)
          .map(([k, v]) => `${k} ${v}`)
          .join(" · ");
        setStatsText(parts ? `Indexed ${s.total_items} · ${parts}` : "Indexed 0");
      })
      .catch(() => undefined);
  }, [items, collecting]);

  async function handleCollect() {
    setCollecting(true);
    setError(null);
    try {
      const result = await api.collect({
        source,
        period_type: periodType,
        period_key: periodKey,
        depth: 1,
      });
      if (result.run && result.run.status === "failed") {
        throw new Error("수집에 실패했습니다. GitHub Token 또는 네트워크를 확인하세요.");
      }
      const [periodRes, trendRes] = await Promise.all([
        api.periods(source, periodType),
        api.trends({
          source,
          periodType,
          periodKey,
          severity: severity || undefined,
          q: deferredQuery || undefined,
        }),
      ]);
      setPeriods(periodRes.periods);
      setItems(trendRes.items);
      setActivePeriodKey(trendRes.period_key);
    } catch (err) {
      setError(err instanceof Error ? err.message : "수집 실패");
    } finally {
      setCollecting(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <RadarStage />
        <p style={{ margin: "0 0 0.75rem", fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--ink-soft)" }}>
          SIGNAL · TREND RADAR
        </p>
        <h1 className="hero-brand">radar_everything</h1>
        <p className="hero-lead">
          GitHub · MCP · 취약점 신호를 주간·월간·연간으로 자동 수집하는 확장형 레이더.
          소스를 플러그인처럼 추가하고, Docker로 바로 띄울 수 있습니다.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" onClick={handleCollect} disabled={collecting}>
            {collecting ? "수집 중…" : "지금 수집"}
          </button>
          <a className="btn btn-ghost" href="#setup">
            Clone &amp; run
          </a>
        </div>
      </header>

      <main className="panel">
        <div className="controls">
          <div className="source-tabs" role="tablist" aria-label="소스">
            {sources.map((s) => (
              <button
                key={s.id}
                className={`chip ${source === s.id ? "active" : ""}`}
                onClick={() => {
                  setSource(s.id);
                  setSeverity("");
                }}
              >
                {s.name}
              </button>
            ))}
          </div>

          <div className="period-tabs" role="tablist" aria-label="기간 유형">
            {(Object.keys(PERIOD_LABELS) as PeriodType[]).map((p) => (
              <button
                key={p}
                className={`chip ${periodType === p ? "active" : ""}`}
                onClick={() => setPeriodType(p)}
              >
                {PERIOD_LABELS[p]}
              </button>
            ))}
          </div>

          <div className="period-keys" role="tablist" aria-label="세부 기간">
            {periods.slice(0, periodType === "weekly" ? 12 : periodType === "monthly" ? 12 : 5).map((p) => (
              <button
                key={p.period_key}
                className={`chip ${periodKey === p.period_key ? "soft-active" : ""}`}
                onClick={() => setPeriodKey(p.period_key)}
                title={p.start && p.end ? `${p.start} → ${p.end}` : undefined}
              >
                {p.period_key}
                {p.has_data ? "" : " ·"}
              </button>
            ))}
          </div>

          <div className="toolbar">
            <input
              className="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="제목 · 태그 · 설명 검색"
              aria-label="검색"
            />
            {activeSource?.supports_severity ? (
              <div className="period-tabs">
                {SEVERITIES.map((s) => (
                  <button
                    key={s || "all"}
                    className={`chip ${severity === s ? "active" : ""}`}
                    onClick={() => setSeverity(s)}
                  >
                    {s || "전체 심각도"}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        </div>

        <div className="meta-row">
          <span>
            구간 <strong>{activePeriodKey || "—"}</strong>
          </span>
          <span>
            결과 <strong>{items.length}</strong>
          </span>
          <span>{statsText}</span>
          {activeSource?.description ? <span>{activeSource.description}</span> : null}
        </div>

        <TrendList items={items} loading={loading} error={error} />
      </main>

      <footer className="footer-note" id="setup">
        <strong>로컬 실행:</strong> <code>docker compose up --build</code> → http://localhost:8080
        <br />
        새 소스 추가: <code>backend/app/collectors/</code>에 <code>BaseCollector</code> 구현 후
        registry에 등록하면 됩니다. GitHub Token / NVD API Key는 선택 사항이며, 없어도 기본 수집이
        동작합니다.
      </footer>
    </div>
  );
}
