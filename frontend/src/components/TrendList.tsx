import type { TrendItem } from "../api/client";

function formatScore(score: number): string {
  if (score >= 1000) return `${(score / 1000).toFixed(score >= 10000 ? 0 : 1)}k`;
  if (Number.isInteger(score)) return String(score);
  return score.toFixed(1);
}

type Props = {
  items: TrendItem[];
  loading: boolean;
  error: string | null;
};

export function TrendList({ items, loading, error }: Props) {
  if (loading) return <div className="loading">레이더 스캔 중…</div>;
  if (error) return <div className="error">{error}</div>;
  if (!items.length) {
    return (
      <div className="empty">
        이 구간에 데이터가 없습니다. 상단의 <strong>지금 수집</strong>을 눌러 주세요.
      </div>
    );
  }

  return (
    <ol className="list">
      {items.map((item, index) => (
        <li
          key={`${item.source}-${item.external_id}-${item.period_key}`}
          className="row"
          style={{ animationDelay: `${Math.min(index, 12) * 0.04}s` }}
        >
          <div className="rank">#{item.rank || index + 1}</div>
          <div>
            <h3 className="row-title">
              <a href={item.url} target="_blank" rel="noreferrer">
                {item.title}
              </a>
            </h3>
            {item.description ? <p className="row-desc">{item.description}</p> : null}
            {item.tags.length ? (
              <div className="tags">
                {item.tags.slice(0, 8).map((tag) => (
                  <span className="tag" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
          <div className="score-block">
            <div className="score-value">{formatScore(item.score)}</div>
            <span className="score-label">{item.score_label}</span>
            {item.severity ? (
              <span className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</span>
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}
