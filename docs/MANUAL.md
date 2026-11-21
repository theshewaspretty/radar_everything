# radar_everything 매뉴얼

이 문서는 **사용 · 운영 · 개발 · 트러블슈팅**까지 한 번에 다루는 상세 매뉴얼입니다.  
빠른 시작만 필요하면 [README.md](../README.md)를 보세요.

---

## 목차

1. [개요](#1-개요)
2. [시스템 요구사항](#2-시스템-요구사항)
3. [설치와 실행](#3-설치와-실행)
4. [UI 사용 가이드](#4-ui-사용-가이드)
5. [소스별 수집 방식](#5-소스별-수집-방식)
6. [설정(환경 변수)](#6-설정환경-변수)
7. [API 레퍼런스](#7-api-레퍼런스)
8. [스케줄러와 데이터](#8-스케줄러와-데이터)
9. [새 소스 추가하기](#9-새-소스-추가하기)
10. [로컬 개발 워크플로](#10-로컬-개발-워크플로)
11. [배포 가이드](#11-배포-가이드)
12. [트러블슈팅](#12-트러블슈팅)
13. [FAQ](#13-faq)
14. [보안 · 윤리](#14-보안--윤리)

---

## 1. 개요

### 1.1 무엇을 하나요?

`radar_everything`은 여러 외부 소스에서 “지금 주목할 신호”를 모아 **기간별 랭킹**으로 보여주는 웹 애플리케이션입니다.

| 소스 ID | 이름 | 랭킹 기준 |
|---------|------|-----------|
| `github` | GitHub | stars |
| `mcp` | MCP Servers | stars (+ registry) |
| `vulnerability` | 취약점 (KISA / CVE) | priority / CVSS · 심각도 |

공통으로 **주간 · 월간 · 연간** 타임라인을 지원하며, 주간/월간은 각각 개별 주·월을 선택할 수 있습니다.

### 1.2 아키텍처

```
┌─────────────────┐     HTTP      ┌──────────────────────┐
│  React Frontend │ ─────────────▶│  FastAPI Backend     │
│  (Vite build)   │◀───────────── │  /api/*              │
└─────────────────┘               │                      │
                                  │  Collector Plugins   │
                                  │   ├─ github          │
                                  │   ├─ mcp             │
                                  │   └─ vulnerability   │
                                  │                      │
                                  │  SQLite (/data)      │
                                  │  APScheduler         │
                                  └──────────────────────┘
```

Docker 이미지에는 프론트 정적 파일이 포함되어, **컨테이너 하나**로 UI+API를 제공합니다.

---

## 2. 시스템 요구사항

### Docker 실행 (권장)

- Docker Desktop 또는 Docker Engine 24+
- Docker Compose v2+
- 여유 메모리 약 512MB 이상 (빌드 시 1GB+ 권장)
- 외부 HTTPS 접근 (GitHub / NVD / 보호나라)

### 로컬 개발

| 구성 요소 | 버전 |
|-----------|------|
| Python | 3.11+ (권장 3.12) |
| Node.js | 20+ |
| npm | 10+ |

---

## 3. 설치와 실행

### 3.1 Clone

```bash
git clone https://github.com/<your-account>/radar_everything.git
cd radar_everything
```

### 3.2 환경 파일

```bash
cp .env.example .env
```

최소 권장 설정:

```env
GITHUB_TOKEN=ghp_your_token_here
PORT=8080
COLLECT_ON_STARTUP=true
ENABLED_SOURCES=github,mcp,vulnerability
```

#### GitHub Token 발급 (권장)

1. GitHub → Settings → Developer settings → Personal access tokens  
2. Fine-grained 또는 classic token 생성  
3. public repo 읽기 권한이면 충분합니다  
4. `.env`의 `GITHUB_TOKEN`에 붙여넣기  

토큰이 없어도 동작하지만, 비인증 요청은 **시간당 약 60회**로 제한됩니다.

### 3.3 Docker Compose로 기동

```bash
docker compose up --build -d
```

확인:

```bash
docker compose ps
curl http://localhost:8080/api/health
```

정상 응답 예:

```json
{"status":"ok","version":"1.0.0","sources":["github","mcp","vulnerability"]}
```

브라우저: [http://localhost:8080](http://localhost:8080)

### 3.4 로그 보기

```bash
docker compose logs -f app
```

### 3.5 중지 / 재시작

```bash
docker compose stop
docker compose start
docker compose down          # 컨테이너 제거 (volume 데이터는 유지)
docker compose down -v       # DB volume까지 삭제 (주의)
```

---

## 4. UI 사용 가이드

### 4.1 첫 화면

- 브랜드: **radar_everything**
- **지금 수집**: 현재 선택된 소스·기간을 즉시 다시 긁어옵니다
- **Clone & run**: 하단 실행 안내로 이동합니다

### 4.2 소스 선택

상단 칩에서 소스를 바꿉니다.

- **GitHub** — 인기 저장소
- **MCP Servers** — MCP 관련 서버/레포
- **취약점 (KISA / CVE)** — 보호나라 + NVD

### 4.3 기간 유형

| 탭 | period_type | 예시 period_key |
|----|-------------|-----------------|
| 주간 | `weekly` | `2026-W47` |
| 월간 | `monthly` | `2026-11` |
| 연간 | `yearly` | `2026` |

세부 기간 칩에 `·` 이 보이면 **아직 데이터가 없는 구간**입니다. **지금 수집**으로 채울 수 있습니다.

### 4.4 검색 · 심각도

- 검색창: 제목 / 설명 / 태그 부분 일치
- 심각도 필터: 취약점 소스에서만 표시 (`critical` / `high` / `medium` / `low`)

### 4.5 결과 행 읽기

- 왼쪽: 순위 (`#1`)
- 가운데: 제목(링크) · 설명 · 태그
- 오른쪽: 점수(`stars` / `cvss` / `priority`) · 심각도 배지

제목을 클릭하면 원문(GitHub / NVD / 보호나라)으로 이동합니다.

---

## 5. 소스별 수집 방식

### 5.1 GitHub (`github`)

1. Search API: `created:START..END stars:>5` 등으로 조회 후 star 정렬  
2. 결과가 비면 Trending 페이지 fallback (`since=weekly|monthly`)  
3. DB에 `period_key` 단위로 upsert(교체 저장)

**해석 팁:** “그 주에 가장 핫하게 떠오른 신규/활동 레포”에 가깝습니다.  
순수 “7일간 star 증가량 TOP”과는 다를 수 있습니다.

### 5.2 MCP (`mcp`)

1. GitHub에서 `topic:mcp-server`, `topic:mcp` 등 검색  
2. 결과가 빈약하면 공식 Registry (`registry.modelcontextprotocol.io`)로 보강  
3. star가 있는 항목을 우선 랭킹

### 5.3 취약점 (`vulnerability`)

1. 보호나라 RSS  
   - 취약점 정보: `bbsId=B0000302`  
   - 보안공지: `bbsId=B0000133`  
2. 제목/본문에서 `CVE-YYYY-NNNNN` 추출  
3. NVD API로 CVSS · severity 보강  
4. 심각도·점수 기준으로 정렬

**심각도 매핑 (CVSS):**

| CVSS | severity |
|------|----------|
| ≥ 9.0 | critical |
| ≥ 7.0 | high |
| ≥ 4.0 | medium |
| > 0 | low |

---

## 6. 설정(환경 변수)

`.env` 또는 `docker-compose.yml`의 `environment`로 주입합니다.

| 변수 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `APP_NAME` | str | `radar_everything` | 앱 표시 이름 |
| `APP_VERSION` | str | `1.0.0` | 버전 |
| `DATABASE_URL` | str | SQLite 경로 | Docker에선 `/data/radar_everything.db` |
| `GITHUB_TOKEN` | str | empty | GitHub API 토큰 |
| `NVD_API_KEY` | str | empty | NVD API 키 |
| `ENABLED_SOURCES` | csv | `github,mcp,vulnerability` | 켤 소스 ID |
| `COLLECT_ON_STARTUP` | bool | `true` | 기동 직후 수집 |
| `COLLECT_CRON_HOURS` | csv | `6,18` | UTC 기준 스케줄 시각 |
| `DEFAULT_LIMIT` | int | `30` | 기본 수집 개수 |
| `PORT` | int | `8080` | 호스트 포트 매핑 |
| `CORS_ORIGINS` | csv | localhost들 | CORS allow list |
| `DEBUG` | bool | `false` | 디버그 모드 |

### 소스만 골라 켜기

```env
ENABLED_SOURCES=github,vulnerability
```

MCP를 끄고 GitHub·취약점만 돌릴 때 유용합니다.

### 스케줄 예시

한국 시간 기준으로 보이게 맞추려면 UTC 변환이 필요합니다.

예) 매일 KST 15:00, 03:00 ≈ UTC 06:00, 18:00 (기본값)

```env
COLLECT_CRON_HOURS=0,12
```

---

## 7. API 레퍼런스

Base URL 예: `http://localhost:8080`

대화형 문서: `http://localhost:8080/docs` (Swagger)

### 7.1 Health

```http
GET /api/health
```

### 7.2 Sources

```http
GET /api/sources
```

응답에 각 소스의 `supports_periods`, `supports_severity`, `last_collected_at`이 포함됩니다.

### 7.3 Periods

```http
GET /api/periods/{source}/{period_type}?depth=16
```

- `period_type`: `weekly` | `monthly` | `yearly`
- `has_data`: 해당 키로 저장된 결과가 있는지

### 7.4 Trends

```http
GET /api/trends/{source}?period_type=weekly&period_key=2026-W47&limit=30&q=react&severity=high
```

| 쿼리 | 설명 |
|------|------|
| `period_type` | 주/월/연 |
| `period_key` | 생략 시 최신 데이터 구간 |
| `limit` | 1–100 |
| `q` | 검색어 |
| `severity` | 취약점 필터 |

### 7.5 Collect

비동기(기본):

```http
POST /api/collect
Content-Type: application/json

{
  "source": "github",
  "period_type": "weekly",
  "period_key": "2026-W47",
  "limit": 30
}
```

동기(UI가 사용):

```http
POST /api/collect?sync=true
```

전체 활성 소스 × 최근 구간 일괄:

```json
{ "depth": 1 }
```

### 7.6 Runs / Stats

```http
GET /api/runs?limit=20
GET /api/stats
```

---

## 8. 스케줄러와 데이터

### 8.1 스케줄

- APScheduler (AsyncIO)
- Cron: 지정된 UTC hour의 0분
- 작업: 활성 소스에 대해 현재 주/월/년(`depth=1`) 수집

### 8.2 저장소

| 환경 | DB 위치 |
|------|---------|
| Docker | volume `radar_everything_data` → `/data/radar_everything.db` |
| 로컬 기본 | `./data/radar_everything.db` (실행 cwd 기준) |

주요 테이블:

- `trend_items` — 랭킹 아이템
- `collect_runs` — 수집 실행 이력
- `source_meta` — 소스 메타/마지막 수집 시각

동일 `(source, external_id, period_type, period_key)`는 재수집 시 교체됩니다.

### 8.3 백업

```bash
docker compose cp app:/data/radar_everything.db ./backup-radar.db
```

또는 volume 백업 도구를 사용하세요.

---

## 9. 새 소스 추가하기

### 9.1 체크리스트

1. `backend/app/collectors/my_source.py` 작성  
2. `CollectedItem` 리스트 반환  
3. `registry.py`에 등록  
4. `ENABLED_SOURCES`에 ID 추가  
5. (선택) UI 문구는 소스 `name`/`description`으로 자동 반영  

### 9.2 최소 코드

```python
from app.collectors.base import BaseCollector, CollectedItem, PeriodWindow

class MyCollector(BaseCollector):
    source_id = "my_source"
    name = "My Source"
    description = "설명"
    supports_periods = ("weekly", "monthly", "yearly")

    async def collect(self, window: PeriodWindow, limit: int = 30) -> list[CollectedItem]:
        return [
            CollectedItem(
                external_id="id-1",
                title="Hello",
                url="https://example.com",
                score=100,
                score_label="likes",
                description="...",
                tags=["demo"],
            )
        ][:limit]
```

`registry.py`:

```python
from app.collectors.my_source import MyCollector
register(MyCollector())
```

템플릿 전문: `backend/app/collectors/example_plugin.py`

### 9.3 설계 팁

- `score`는 정렬 가능한 숫자로 통일
- `score_label`로 UI 단위 표시 (`stars`, `likes`, `cvss` …)
- 취약점류는 `severity`와 `supports_severity = True` 설정
- 외부 API 실패는 예외를 삼키고 로그만 남기면 부분 성공이 가능합니다 (서비스 레이어가 run status를 기록)

---

## 10. 로컬 개발 워크플로

### 10.1 Backend only

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
$env:COLLECT_ON_STARTUP='false'
$env:DATABASE_URL='sqlite:///./data/radar_everything.db'
uvicorn app.main:app --reload --port 8000
```

수동 수집 테스트:

```bash
curl -X POST "http://localhost:8000/api/collect?sync=true" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"github\",\"period_type\":\"weekly\",\"limit\":10}"
```

### 10.2 Frontend only

```bash
cd frontend
npm install
npm run dev
```

### 10.3 프로덕션 빌드 확인

```bash
cd frontend
npm run build
# dist/ 를 backend/static 으로 복사하면 단일 프로세스로도 서빙 가능
```

Docker 빌드는 이 과정을 Dockerfile에서 자동 수행합니다.

---

## 11. 배포 가이드

### 11.1 로컬 / 사내 서버

```bash
docker compose up --build -d
```

리버스 프록시(Nginx/Caddy)에서 `8080`으로 프록시하면 됩니다.

### 11.2 공개 서버 체크리스트

- [ ] `GITHUB_TOKEN` / `NVD_API_KEY`를 시크릿으로 주입 (이미지에 굽지 말 것)
- [ ] `.env`를 git에 커밋하지 말 것
- [ ] HTTPS 종료(TLS)
- [ ] 방화벽에서 필요한 포트만 개방
- [ ] `COLLECT_CRON_HOURS`를 트래픽/쿼터에 맞게 조정
- [ ] volume 백업 주기 설정

### 11.3 GitHub public 레포로 공유

1. 빈 public 저장소 `radar_everything` 생성  
2. [GITHUB_LISTING.md](./GITHUB_LISTING.md)의 Description / Topics 붙여넣기  
3. 코드 push  
4. README의 clone URL을 실제 계정명으로 수정  

### 11.4 GitHub Pages 켜기

랜딩 사이트 소스: 레포 루트 `site/`  
워크플로: `.github/workflows/pages.yml`

1. GitHub 레포 → **Settings → Pages**  
2. **Build and deployment → Source** 를 **GitHub Actions** 로 설정  
3. `main`/`master`에 push하거나 Actions에서 **Deploy GitHub Pages** 워크플로를 수동 실행  
4. 배포 URL: `https://<user>.github.io/radar_everything/`  
5. (선택) About의 Website 필드에 Pages URL 입력  

**주의:** Pages는 정적 HTML만 호스팅합니다. 수집 API·스케줄러·DB가 포함된 풀앱은 `docker compose up` 으로 실행해야 합니다.

로컬 미리보기:

```bash
cd site
python -m http.server 5500
```

---

## 12. 트러블슈팅

### 화면은 뜨는데 결과가 비어 있음

1. **지금 수집** 클릭  
2. `docker compose logs -f app` 에서 `failed` / `rate limit` 확인  
3. `GITHUB_TOKEN` 설정 여부 확인  
4. `/api/runs`로 최근 수집 상태 확인  

```bash
curl http://localhost:8080/api/runs
```

### GitHub 403 / rate limit

- 토큰 추가 또는 수집 빈도 감소 (`COLLECT_ON_STARTUP=false`, cron 축소)
- 한 번에 모든 과거 주를 긁지 말고 `depth=1`부터

### 취약점만 안 됨

- 보호나라 RSS 접근 가능 여부 (회사망/방화벽)
- NVD는 키가 없어도 되지만 제한이 더 큼 → `NVD_API_KEY` 권장

### Docker 빌드 중 npm/esbuild OOM

- Docker Desktop 메모리 할당을 늘리기 (4GB+)
- 이미 빌드된 이미지 재사용: `docker compose up -d` (캐시 활용)

### 포트 충돌

```env
PORT=9090
```

```bash
docker compose up -d
# http://localhost:9090
```

### DB 초기화하고 싶을 때

```bash
docker compose down -v
docker compose up --build -d
```

---

## 13. FAQ

**Q. Windows / macOS / Linux 모두 되나요?**  
A. 네. Docker만 있으면 OS 무관하게 동일하게 실행됩니다.

**Q. 반드시 GitHub 토큰이 필요한가요?**  
A. 필수는 아닙니다. 다만 실사용·데모·다중 수집에는 강력 권장합니다.

**Q. 주간 랭킹이 GitHub Trending과 다르데요?**  
A. 정상입니다. 본 프로젝트는 Search 기반 기간 필터 + fallback을 쓰며, 공식 Trending 알고리즘과 동일하지 않습니다.

**Q. 다른 사이트도 붙일 수 있나요?**  
A. 가능합니다. Collector 플러그인으로 RSS/API/크롤링을 추가하세요. (법적·ToS 준수 필수)

**Q. PostgreSQL로 바꿀 수 있나요?**  
A. `DATABASE_URL`을 SQLAlchemy 호환 URL로 바꾸면 됩니다. (예: `postgresql+psycopg://...`) 필요 시 드라이버를 `requirements.txt`에 추가하세요.

**Q. 프론트만 다른 도메인에 둘 수 있나요?**  
A. 가능합니다. `CORS_ORIGINS`에 프론트 origin을 추가하고 API base URL을 맞춰 주세요.

---

## 14. 보안 · 윤리

- 토큰/키는 환경변수·시크릿으로만 관리하고 커밋하지 마세요.
- 수집은 공개 데이터/공식 API·RSS를 전제로 합니다.
- 과도한 요청으로 상대 서비스에 부하를 주지 마세요.
- 취약점 정보는 방어·모니터링 목적에 맞게 사용하세요.
- 스크래핑이 필요한 소스 추가 시 해당 사이트 ToS·robots 정책을 확인하세요.

---

## 변경 이력

| 버전 | 내용 |
|------|------|
| 1.0.0 | 최초 public 버전 — GitHub / MCP / Vulnerability + Docker |

문의·개선 제안은 GitHub Issues로 남겨 주세요.
