# radar_everything

**무엇이든 레이더에 올려라.**  
GitHub 스타 · MCP 인기 서버 · 취약점(CVE/CVSS/보호나라) 같은 외부 신호를 **주간 / 월간 / 연간**으로 자동 수집·랭킹하는 확장형 웹앱입니다.

- **풀스택 앱**: Docker 한 줄로 로컬/서버 실행 (수집 · 스케줄 · DB)
- **GitHub Pages 데모**: 브라우저에서 UI·샘플·(선택) GitHub 라이브 조회 체험
- **플러그인 소스**: `BaseCollector` 추가만으로 확장

[매뉴얼](./docs/MANUAL.md) · [GitHub 소개 문구](./docs/GITHUB_LISTING.md) · [Pages 안내](./site/README.md) · [라이선스](./LICENSE)

---

## 한눈에 보기

| 항목 | 내용 |
|------|------|
| 프로젝트명 | `radar_everything` |
| 목적 | 여러 소스의 인기/스타/심각도 신호를 기간별로 자동 수집 |
| 기본 소스 | GitHub, MCP Servers, 취약점(KISA 보호나라 + NVD) |
| 기간 | 주간(각 주) · 월간(각 월) · 연간 |
| 풀스택 | FastAPI · React(Vite) · SQLite · Docker Compose |
| Pages | 랜딩(`site/`) + 정적 데모 앱(`site/app/`) |
| 라이선스 | MIT |

### 실행 방식 비교

| | Docker 풀스택 | GitHub Pages 데모 |
|--|---------------|-------------------|
| URL 예 | `http://localhost:8080` | `https://<user>.github.io/radar_everything/app/` |
| UI | ✅ | ✅ |
| 샘플 데이터 | 기동 후 수집 | ✅ `snapshot.json` |
| GitHub/MCP 라이브 수집 | ✅ 서버 | ✅ 브라우저→GitHub API |
| 취약점(KISA/NVD) 라이브 | ✅ | ❌ (샘플만, CORS) |
| 스케줄러 · SQLite | ✅ | ❌ |
| 용도 | 실제 운영/로컬 사용 | 공개 데모 · UI 체험 |

---

## 왜 radar_everything 인가?

- **Everything**: GitHub만이 아니라 MCP·취약점 등 관심 신호를 같은 UX로 묶습니다.
- **Radar**: 주/월/연 타임라인에서 “지금 튀는 신호”를 빠르게 스캔합니다.
- **Extensible**: Collector 플러그인 하나로 UI·API·스케줄러에 연결됩니다.
- **Clone & Run / Try Online**: Docker로 바로 돌리거나, Pages 데모로 먼저 체험합니다.

---

## 주요 기능

### 1) GitHub Radar
- 선택한 주/월/년 구간의 공개 저장소를 star 기준 랭킹
- GitHub Search API 우선, 실패 시 Trending HTML fallback
- 언어 · 토픽 등 메타데이터 포함

### 2) MCP Radar
- `mcp-server` 등 MCP 관련 저장소를 star 기준 수집
- 공식 MCP Registry 메타로 결과 보강

### 3) Vulnerability Radar
- [보호나라(boho.or.kr)](https://www.boho.or.kr/) RSS (취약점·보안공지)
- NVD CVE API로 CVSS / 심각도 보강
- Critical → High → Medium → Low 필터

### 4) 운영 · 확장
- 기동 시 자동 수집, UTC 스케줄 수집
- UI **지금 수집** / REST API
- 새 소스는 `BaseCollector` 플러그인으로 추가

### 5) GitHub Pages 데모
- 실제 React UI와 동일한 화면
- 샘플 랭킹 + GitHub/MCP 브라우저 라이브 조회(선택)
- Actions로 랜딩·데모 자동 배포

---

## GitHub Pages (랜딩 + 데모 앱)

### 활성화

1. 레포 **Settings → Pages → Source: GitHub Actions**
2. `main` / `master`에 push (또는 Actions에서 **Deploy GitHub Pages** 수동 실행)
3. 접속
   - 소개: `https://<your-account>.github.io/radar_everything/`
   - **데모 앱**: `https://<your-account>.github.io/radar_everything/app/`

워크플로: [`.github/workflows/pages.yml`](./.github/workflows/pages.yml)  
데모 앱은 `site/app/`에 포함되어 있습니다. (Actions가 다시 빌드하거나, 로컬에서 `frontend`를 빌드해 복사)

데모가 안 보이면:
1. `https://<user>.github.io/<repo>/app/` 로 직접 접속
2. 최신 커밋에 `site/app/index.html`이 있는지 확인
3. Pages Source가 **GitHub Actions** 또는 **`/site` 폴더**인지 확인 후 재배포

### 데모에서 되는 것 / 안 되는 것

| 가능 | 제한 |
|------|------|
| 소스·주/월/연·검색·심각도 UI | 서버 스케줄러·SQLite 없음 |
| `demo-data/snapshot.json` 샘플 | 취약점 라이브 RSS/NVD 불가 (CORS) |
| GitHub/MCP 「데모 수집」= 브라우저 GitHub API | 비인증 rate limit(~60/hr) 가능 → 샘플 폴백 |

### 로컬에서 데모 UI만

```bash
cd frontend
npm install
npm run dev:demo
```

자세한 내용은 [site/README.md](./site/README.md), [매뉴얼 §11.4](./docs/MANUAL.md#114-github-pages-켜기-랜딩--데모-앱)를 보세요.

---

## 60초 Quick Start (Docker 풀스택)

```bash
git clone https://github.com/<your-account>/radar_everything.git
cd radar_everything
cp .env.example .env
```

```env
# .env (권장)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
# NVD_API_KEY=
PORT=8080
```

```bash
docker compose up --build -d
```

→ **http://localhost:8080**

```bash
docker compose down       # 중지
docker compose up -d      # 데이터 유지 재시작
docker compose logs -f app
```

> 토큰 없이도 동작하지만, GitHub API rate limit(비인증 ~60 req/hr) 때문에 토큰을 권장합니다.

---

## 화면 사용법 (요약)

1. 소스 탭: **GitHub / MCP / 취약점**
2. 기간: **주간 · 월간 · 연간**
3. 세부 기간 칩: `2026-W47` / `2026-11` / `2026` …
4. 검색 · (취약점) 심각도 필터
5. 데이터가 비면 **지금 수집** (Pages에서는 **데모 수집**)

Pages 데모 상단에는 노란 **Pages Demo** 배너가 표시됩니다.

전체 UI 설명: [매뉴얼 §4](./docs/MANUAL.md#4-ui-사용-가이드)

---

## 로컬 개발 (Docker 없이)

### Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate

pip install -r requirements.txt
# PowerShell
$env:COLLECT_ON_STARTUP='false'
uvicorn app.main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

### Frontend (백엔드 연동)

```bash
cd frontend
npm install
npm run dev
```

→ http://localhost:5173 (`/api` → `8000` 프록시)

### Frontend (Pages와 같은 데모 모드)

```bash
cd frontend
npm run dev:demo
```

---

## API 요약 (Docker / 로컬 백엔드)

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/api/health` | 헬스체크 |
| `GET` | `/api/sources` | 소스 목록 |
| `GET` | `/api/periods/{source}/{period_type}` | 기간 키 목록 |
| `GET` | `/api/trends/{source}` | 랭킹 |
| `POST` | `/api/collect?sync=true` | 즉시 수집 |
| `GET` | `/api/runs` | 수집 이력 |
| `GET` | `/api/stats` | 통계 |

```bash
curl -X POST "http://localhost:8080/api/collect?sync=true" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"github\",\"period_type\":\"weekly\"}"

curl "http://localhost:8080/api/trends/github?period_type=weekly&period_key=2026-W47&limit=20"
```

상세: [매뉴얼 API](./docs/MANUAL.md#7-api-레퍼런스)

> Pages 데모는 백엔드 API 없이 `frontend/src/api/demo.ts` + `snapshot.json`으로 동작합니다.

---

## 새 소스 추가 (플러그인)

1. `backend/app/collectors/my_source.py`에 `BaseCollector` 구현  
2. `registry.py`에서 `register(MyCollector())`  
3. `.env`의 `ENABLED_SOURCES`에 ID 추가  

템플릿: [`backend/app/collectors/example_plugin.py`](./backend/app/collectors/example_plugin.py)

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `GITHUB_TOKEN` | (empty) | GitHub API 인증 (권장) |
| `NVD_API_KEY` | (empty) | NVD CVE API 키 |
| `ENABLED_SOURCES` | `github,mcp,vulnerability` | 활성 소스 |
| `COLLECT_ON_STARTUP` | `true` | 기동 시 수집 |
| `COLLECT_CRON_HOURS` | `6,18` | 스케줄 (UTC) |
| `DEFAULT_LIMIT` | `30` | 기본 개수 |
| `PORT` | `8080` | 호스트 포트 |
| `DATABASE_URL` | SQLite | DB URL |
| `CORS_ORIGINS` | localhost… | CORS |
| `APP_NAME` | `radar_everything` | 앱 이름 |

전체 표: [매뉴얼 §6](./docs/MANUAL.md#6-설정환경-변수)

프론트 데모 빌드용(CI):

| 변수 | 설명 |
|------|------|
| `VITE_DEMO_MODE=true` | 데모 API 사용 |
| `VITE_BASE=/<repo>/app/` | Pages 하위 경로 |

---

## 프로젝트 구조

```
radar_everything/
├── backend/app/
│   ├── api/              # REST
│   ├── collectors/       # 소스 플러그인 (github, mcp, vulnerability, example)
│   ├── models/
│   ├── services/         # 수집 · 조회 · 스케줄
│   └── core/
├── frontend/             # React 앱
│   ├── public/demo-data/ # Pages 데모용 snapshot.json
│   └── src/api/demo.ts   # 데모 모드 클라이언트
├── site/                 # Pages 랜딩 (+ CI가 app/ 채움)
├── docs/
│   ├── MANUAL.md
│   └── GITHUB_LISTING.md
├── .github/workflows/pages.yml
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

---

## 한계와 주의

- GitHub “기간 내 star 증가량” 공식 API는 없어, **기간 내 생성/활동 저장소 star 랭킹**(+ Trending fallback)을 사용합니다.
- 비인증 GitHub API rate limit이 낮습니다. 운영·다수 수집 시 토큰을 쓰세요.
- NVD 날짜 필터는 약 120일 제한 → 연간 CVE는 창 후반 기준입니다.
- 보호나라 RSS/HTML 구조 변경 시 파서가 깨질 수 있습니다.
- Pages 데모는 **공개 체험용**이며 풀 수집 파이프라인을 대체하지 않습니다.
- 각 API/사이트 ToS · rate limit을 준수하세요.

---

## 기여

1. fork → feature 브랜치  
2. Docker 또는 `dev` / `dev:demo`로 확인  
3. 작은 단위 PR  

새 소스는 `example_plugin.py` 패턴을 따라 주세요.

---

## 관련 문서

| 문서 | 내용 |
|------|------|
| [docs/MANUAL.md](./docs/MANUAL.md) | 설치·UI·API·Pages 데모·트러블슈팅 |
| [docs/GITHUB_LISTING.md](./docs/GITHUB_LISTING.md) | Description / Topics / 홍보 문구 |
| [site/README.md](./site/README.md) | Pages 랜딩·데모 배포 |
| [.env.example](./.env.example) | 환경변수 예시 |

---

## License

[MIT](./LICENSE)
