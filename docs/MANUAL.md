# radar_everything 매뉴얼

이 문서는 **사용 · 운영 · 개발 · GitHub Pages 데모 · 트러블슈팅**을 다루는 상세 매뉴얼입니다.  
빠른 시작만 필요하면 [README.md](../README.md)를 보세요.

---

## 목차

1. [개요](#1-개요)
2. [시스템 요구사항](#2-시스템-요구사항)
3. [설치와 실행 (Docker 풀스택)](#3-설치와-실행-docker-풀스택)
4. [UI 사용 가이드](#4-ui-사용-가이드)
5. [소스별 수집 방식](#5-소스별-수집-방식)
6. [설정(환경 변수)](#6-설정환경-변수)
7. [API 레퍼런스](#7-api-레퍼런스)
8. [스케줄러와 데이터](#8-스케줄러와-데이터)
9. [새 소스 추가하기](#9-새-소스-추가하기)
10. [로컬 개발 워크플로](#10-로컬-개발-워크플로)
11. [배포 가이드](#11-배포-가이드)
12. [GitHub Pages 데모 앱](#12-github-pages-데모-앱)
13. [트러블슈팅](#13-트러블슈팅)
14. [FAQ](#14-faq)
15. [보안 · 윤리](#15-보안--윤리)

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

### 1.2 두 가지 실행 형태

| | Docker 풀스택 | GitHub Pages 데모 |
|--|---------------|-------------------|
| 목적 | 실제 수집·운영 | 공개 UI 체험 |
| 백엔드 | FastAPI + SQLite + Scheduler | 없음 (정적) |
| 데이터 | 라이브 수집 | `snapshot.json` + (선택) 브라우저 GitHub API |
| 취약점 라이브 | 가능 | 불가 (CORS → 샘플) |
| URL 예 | `http://localhost:8080` | `…/radar_everything/app/` |

### 1.3 아키텍처

**풀스택 (Docker)**

```
┌─────────────────┐     HTTP      ┌──────────────────────┐
│  React Frontend │ ─────────────▶│  FastAPI Backend     │
│  (Vite build)   │◀───────────── │  /api/*              │
└─────────────────┘               │  Collectors          │
                                  │   ├─ github          │
                                  │   ├─ mcp             │
                                  │   └─ vulnerability   │
                                  │  SQLite + Scheduler  │
                                  └──────────────────────┘
```

**Pages 데모**

```
┌──────────────────────────────┐
│  Static site (GitHub Pages)  │
│  /           → 랜딩 (site/)  │
│  /app/       → React 데모    │
│     ├─ demo.ts               │
│     └─ demo-data/snapshot.json
│  (GitHub/MCP 수집 시)        │
│     └─ 브라우저 → api.github.com
└──────────────────────────────┘
```

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

### GitHub Pages 데모만 볼 때

- 최신 브라우저만 있으면 됩니다 (서버 불필요).

---

## 3. 설치와 실행 (Docker 풀스택)

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

### 3.4 로그 / 중지 / 재시작

```bash
docker compose logs -f app
docker compose stop
docker compose start
docker compose down          # volume 데이터 유지
docker compose down -v       # DB까지 삭제 (주의)
```

---

## 4. UI 사용 가이드

### 4.1 첫 화면 (공통)

- 브랜드: **radar_everything**
- **지금 수집** / Pages에서는 **데모 수집**
- **Clone & run**: Docker Quick Start 안내로 이동

### 4.2 Pages Demo 배너

데모 모드(`VITE_DEMO_MODE=true`)에서는 상단에 안내 배너가 표시됩니다.

- 샘플 데이터로 UI 체험
- GitHub/MCP 데모 수집 = 브라우저→GitHub API
- 풀 자동 수집은 Docker 안내 링크

### 4.3 소스 선택

- **GitHub** — 인기 저장소  
- **MCP Servers** — MCP 관련 서버/레포  
- **취약점 (KISA / CVE)** — 보호나라 + NVD (풀스택) / 샘플(데모)

### 4.4 기간 유형

| 탭 | period_type | 예시 period_key |
|----|-------------|-----------------|
| 주간 | `weekly` | `2026-W47` |
| 월간 | `monthly` | `2026-11` |
| 연간 | `yearly` | `2026` |

세부 기간 칩에 `·` 이 보이면 **아직 데이터가 없는 구간**입니다. 수집 버튼으로 채울 수 있습니다.

### 4.5 검색 · 심각도

- 검색: 제목 / 설명 / 태그  
- 심각도: 취약점 소스에서만 (`critical` / `high` / `medium` / `low`)

### 4.6 결과 행

- 왼쪽: 순위 `#1`  
- 가운데: 제목(링크) · 설명 · 태그  
- 오른쪽: 점수(`stars` / `cvss` / `priority`) · 심각도 배지  

---

## 5. 소스별 수집 방식

### 5.1 GitHub (`github`) — 풀스택

1. Search API: `created:START..END stars:>5` 등 → star 정렬  
2. 비면 Trending HTML fallback  
3. DB에 `period_key` 단위로 교체 저장  

**해석:** “그 주에 핫한 신규/활동 레포”에 가깝습니다. 공식 “7일 star 증가 TOP”과 다를 수 있습니다.

### 5.2 MCP (`mcp`) — 풀스택

1. GitHub `topic:mcp-server` / `topic:mcp` 검색  
2. 빈약하면 공식 Registry 보강  
3. star 우선 랭킹  

### 5.3 취약점 (`vulnerability`) — 풀스택

1. 보호나라 RSS (`B0000302`, `B0000133`)  
2. CVE ID 추출  
3. NVD CVSS · severity 보강  
4. 심각도·점수 정렬  

| CVSS | severity |
|------|----------|
| ≥ 9.0 | critical |
| ≥ 7.0 | high |
| ≥ 4.0 | medium |
| > 0 | low |

### 5.4 Pages 데모에서의 수집

| 소스 | 데모 동작 |
|------|-----------|
| GitHub | 브라우저에서 GitHub Search API 호출 → `sessionStorage` 보관. 실패 시 샘플 |
| MCP | `topic:mcp-server`로 동일. 실패 시 샘플 |
| 취약점 | CORS로 라이브 불가 → `snapshot.json` 갱신만 |

구현: `frontend/src/api/demo.ts`  
샘플: `frontend/public/demo-data/snapshot.json`

---

## 6. 설정(환경 변수)

### 6.1 백엔드 / Docker

`.env` 또는 `docker-compose.yml`의 `environment`로 주입합니다.

| 변수 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `APP_NAME` | str | `radar_everything` | 앱 표시 이름 |
| `APP_VERSION` | str | `1.0.0` | 버전 |
| `DATABASE_URL` | str | SQLite 경로 | Docker: `/data/radar_everything.db` |
| `GITHUB_TOKEN` | str | empty | GitHub API 토큰 |
| `NVD_API_KEY` | str | empty | NVD API 키 |
| `ENABLED_SOURCES` | csv | `github,mcp,vulnerability` | 켤 소스 ID |
| `COLLECT_ON_STARTUP` | bool | `true` | 기동 직후 수집 |
| `COLLECT_CRON_HOURS` | csv | `6,18` | UTC 스케줄 시각 |
| `DEFAULT_LIMIT` | int | `30` | 기본 수집 개수 |
| `PORT` | int | `8080` | 호스트 포트 |
| `CORS_ORIGINS` | csv | localhost들 | CORS |
| `DEBUG` | bool | `false` | 디버그 |

소스만 골라 켜기:

```env
ENABLED_SOURCES=github,vulnerability
```

스케줄 예 (UTC):

```env
COLLECT_CRON_HOURS=0,12
```

### 6.2 프론트 데모 빌드 (Pages CI)

| 변수 | 설명 |
|------|------|
| `VITE_DEMO_MODE=true` | `demo.ts` API 사용 |
| `VITE_BASE=/<repo-name>/app/` | Pages 프로젝트 하위 경로 |
| `VITE_API_BASE` | (풀스택용) API origin. 데모에서는 보통 비움 |

로컬 데모:

```bash
cd frontend
npm run dev:demo    # .env.demo → VITE_DEMO_MODE=true
```

---

## 7. API 레퍼런스

> 이 절은 **Docker / 로컬 백엔드** 기준입니다. Pages 데모는 HTTP `/api`가 없습니다.

Base URL 예: `http://localhost:8080`  
Swagger: `http://localhost:8080/docs`

### 7.1 Health

```http
GET /api/health
```

### 7.2 Sources

```http
GET /api/sources
```

### 7.3 Periods

```http
GET /api/periods/{source}/{period_type}?depth=16
```

- `period_type`: `weekly` | `monthly` | `yearly`
- `has_data`: 저장된 결과 여부

### 7.4 Trends

```http
GET /api/trends/{source}?period_type=weekly&period_key=2026-W47&limit=30&q=react&severity=high
```

| 쿼리 | 설명 |
|------|------|
| `period_type` | 주/월/연 |
| `period_key` | 생략 시 최신 구간 |
| `limit` | 1–100 |
| `q` | 검색 |
| `severity` | 취약점 필터 |

### 7.5 Collect

```http
POST /api/collect?sync=true
Content-Type: application/json

{
  "source": "github",
  "period_type": "weekly",
  "period_key": "2026-W47",
  "limit": 30
}
```

`sync` 없이 호출하면 백그라운드 실행입니다.  
전체 활성 소스 일괄: `{ "depth": 1 }`

### 7.6 Runs / Stats

```http
GET /api/runs?limit=20
GET /api/stats
```

---

## 8. 스케줄러와 데이터

### 8.1 스케줄 (풀스택만)

- APScheduler (AsyncIO)
- 지정 UTC hour의 0분
- 활성 소스 × 현재 주/월/년 (`depth=1`)

### 8.2 저장소 (풀스택만)

| 환경 | DB |
|------|-----|
| Docker | volume `radar_everything_data` → `/data/radar_everything.db` |
| 로컬 | `./data/radar_everything.db` (cwd 기준) |

테이블: `trend_items`, `collect_runs`, `source_meta`

### 8.3 백업

```bash
docker compose cp app:/data/radar_everything.db ./backup-radar.db
```

### 8.4 데모 데이터

- 정적 파일: `frontend/public/demo-data/snapshot.json`
- 라이브 오버레이: 브라우저 `sessionStorage` (`radar_everything_demo_overlay_v1`)
- 탭을 닫으면 라이브 오버레이는 사라질 수 있습니다.

---

## 9. 새 소스 추가하기

### 9.1 체크리스트 (풀스택)

1. `backend/app/collectors/my_source.py` 작성  
2. `CollectedItem` 반환  
3. `registry.py`에 등록  
4. `ENABLED_SOURCES`에 ID 추가  

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
                tags=["demo"],
            )
        ][:limit]
```

```python
from app.collectors.my_source import MyCollector
register(MyCollector())
```

템플릿: `backend/app/collectors/example_plugin.py`

### 9.3 Pages 데모에 샘플도 넣고 싶다면

1. `frontend/public/demo-data/snapshot.json`의 `sources` · `bundles`에 항목 추가  
2. (선택) `demo.ts`의 `collect()`에 브라우저 가능 API가 있으면 분기 추가  

---

## 10. 로컬 개발 워크플로

### 10.1 Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
$env:COLLECT_ON_STARTUP='false'
$env:DATABASE_URL='sqlite:///./data/radar_everything.db'
uvicorn app.main:app --reload --port 8000
```

```bash
curl -X POST "http://localhost:8000/api/collect?sync=true" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"github\",\"period_type\":\"weekly\",\"limit\":10}"
```

### 10.2 Frontend (API 연동)

```bash
cd frontend
npm install
npm run dev
```

### 10.3 Frontend (Pages 데모 모드)

```bash
cd frontend
npm run dev:demo
```

### 10.4 프로덕션 빌드

```bash
# 풀스택용 (백엔드 연동 가정)
cd frontend && npm run build

# Pages 데모용
cd frontend
# CI는 VITE_DEMO_MODE / VITE_BASE 를 주입
npm run build:demo
```

Docker 이미지 빌드는 루트 `Dockerfile`이 프론트를 함께 넣습니다.  
Pages는 `.github/workflows/pages.yml`이 `site/app/`에 데모 빌드 결과물을 넣습니다.

---

## 11. 배포 가이드

### 11.1 로컬 / 사내 서버 (풀스택)

```bash
docker compose up --build -d
```

Nginx/Caddy에서 `8080`으로 프록시하면 됩니다.

### 11.2 공개 서버 체크리스트

- [ ] `GITHUB_TOKEN` / `NVD_API_KEY`를 시크릿으로 주입 (이미지에 굽지 말 것)
- [ ] `.env`를 git에 커밋하지 말 것
- [ ] HTTPS 종료
- [ ] 필요 포트만 개방
- [ ] 스케줄·쿼터 조정
- [ ] volume 백업

### 11.3 GitHub public 레포

1. public 저장소명 `radar_everything` 권장  
2. [GITHUB_LISTING.md](./GITHUB_LISTING.md) Description / Topics 적용  
3. push  
4. README의 `<your-account>`를 실제 계정으로 수정  

### 11.4 GitHub Pages 켜기 (랜딩 + 데모 앱)

→ 다음 절 **[§12](#12-github-pages-데모-앱)** 참고.

---

## 12. GitHub Pages 데모 앱

### 12.1 구성

| 경로 | 내용 |
|------|------|
| `site/index.html` | 소개 랜딩 (`Open live demo` → `/app/`) |
| `site/app/` | 정적 React 데모 빌드 결과 (저장소에 포함 + CI가 재빌드 가능) |
| `frontend/public/demo-data/snapshot.json` | 샘플 랭킹 |
| `frontend/src/api/demo.ts` | 데모 API |
| `.github/workflows/pages.yml` | 빌드 + Pages 배포 |

### 12.2 활성화 절차

1. 레포 **Settings → Pages**  
2. **Build and deployment → Source = GitHub Actions**  
3. `main`/`master` push 또는 workflow **Deploy GitHub Pages** 수동 실행  
4. 접속  
   - `https://<user>.github.io/radar_everything/`  
   - `https://<user>.github.io/radar_everything/app/`  
5. About → Website에 Pages URL 입력 권장  

CI는 레포 이름에 맞춰 `VITE_BASE=/<repo>/app/` 을 자동 설정합니다.

### 12.3 데모 사용 시나리오

1. 랜딩에서 **Open live demo**  
2. GitHub / MCP / 취약점 탭 탐색  
3. 주·월·연·검색·심각도 확인  
4. **데모 수집**  
   - GitHub·MCP: 가능하면 라이브 결과로 갱신  
   - 취약점: 샘플 리로드  
5. 상단 배너의 **소개 페이지** / **Clone & run**으로 Docker 안내  

### 12.4 한계 (반드시 이해)

- 서버 프로세스·스케줄러·영속 DB 없음  
- 보호나라·NVD는 브라우저 CORS로 막혀 라이브 수집 불가  
- GitHub 비인증 API는 IP당 rate limit → 방문자가 많으면 429 후 샘플 폴백  
- “운영용 레이더”가 아니라 **체험·홍보용**입니다  

### 12.5 샘플 데이터 갱신

`frontend/public/demo-data/snapshot.json`을 수정한 뒤 push하면 다음 Pages 배포에 반영됩니다.  
`bundles.<source>.<period_type>`는 **offset 0 = 현재 주/월/년**에 매핑되는 배열의 배열입니다.

---

## 13. 트러블슈팅

### Docker: 화면은 뜨는데 결과가 비어 있음

1. **지금 수집**  
2. `docker compose logs -f app`  
3. `GITHUB_TOKEN` 확인  
4. `curl http://localhost:8080/api/runs`  

### GitHub 403 / rate limit (Docker 또는 Pages 데모)

- Docker: 토큰 추가, `COLLECT_ON_STARTUP=false`, cron 축소  
- Pages: 잠시 후 재시도, 샘플 폴백이 정상인지 확인  

### 취약점만 안 됨 (Docker)

- 보호나라 RSS 접근(방화벽)  
- `NVD_API_KEY` 권장  

### Pages 데모에서 취약점 라이브가 안 됨

- **정상**입니다. CORS 때문에 샘플만 제공합니다. Docker를 사용하세요.

### Pages `/app/` 가 404

- Actions 워크플로가 성공했는지 확인  
- Source가 **GitHub Actions**인지 확인  
- 레포 이름과 URL 경로가 일치하는지 확인 (`/<repo>/app/`)  

### Docker 빌드 OOM (npm/esbuild)

- Docker Desktop 메모리 4GB+  
- 캐시된 이미지로 `docker compose up -d`  

### 포트 충돌

```env
PORT=9090
```

### DB 초기화

```bash
docker compose down -v
docker compose up --build -d
```

---

## 14. FAQ

**Q. Windows / macOS / Linux 모두 되나요?**  
A. Docker 풀스택은 OS 무관. Pages 데모는 브라우저만 있으면 됩니다.

**Q. Pages만으로 충분한가요?**  
A. UI 체험·홍보에는 충분합니다. 자동 수집·취약점 라이브·DB가 필요하면 Docker를 쓰세요.

**Q. 반드시 GitHub 토큰이 필요한가요?**  
A. 필수는 아닙니다. Docker 실사용·다중 수집에는 강력 권장. Pages 데모는 토큰 없이 브라우저 호출이라 제한이 큽니다.

**Q. 주간 랭킹이 GitHub Trending과 다르데요?**  
A. 정상입니다. Search 기간 필터 + fallback을 쓰며 공식 Trending과 동일하지 않습니다.

**Q. 다른 사이트도 붙일 수 있나요?**  
A. 풀스택은 Collector 플러그인으로 가능. Pages 데모는 샘플 JSON(및 브라우저 CORS 허용 API) 범위에서 확장합니다.

**Q. PostgreSQL로 바꿀 수 있나요?**  
A. `DATABASE_URL`을 SQLAlchemy URL로 변경하고 드라이버를 추가하세요. Pages 데모와는 무관합니다.

**Q. 데모 샘플을 우리 데이터로 바꾸고 싶어요.**  
A. `frontend/public/demo-data/snapshot.json`을 편집한 뒤 Pages를 다시 배포하세요.

---

## 15. 보안 · 윤리

- 토큰/키는 환경변수·시크릿으로만 관리하고 커밋하지 마세요.
- 수집은 공개 데이터/공식 API·RSS를 전제로 합니다.
- Pages 데모의 브라우저→GitHub 호출도 rate limit을 존중하세요.
- 취약점 정보는 방어·모니터링 목적에 맞게 사용하세요.
- 스크래핑 소스 추가 시 ToS·robots를 확인하세요.

---

## 변경 이력

| 버전 | 내용 |
|------|------|
| 1.0.0 | GitHub / MCP / Vulnerability + Docker |
| 1.1.0 | GitHub Pages 랜딩 + 정적 데모 앱 (`/app/`), demo snapshot · live GitHub/MCP |

문의·개선 제안은 GitHub Issues로 남겨 주세요.
