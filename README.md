# radar_everything

**무엇이든 레이더에 올려라.**  
GitHub 스타 · MCP 인기 서버 · 취약점(CVE/CVSS/보호나라) 같은 외부 신호를 **주간 / 월간 / 연간**으로 자동 수집·랭킹하는 확장형 웹앱입니다.

누구나 clone 한 뒤 Docker 한 줄로 로컬에서 바로 실행할 수 있고, 새 데이터 소스는 플러그인처럼 추가할 수 있습니다.

[매뉴얼(자세히)](./docs/MANUAL.md) · [GitHub 소개 문구 모음](./docs/GITHUB_LISTING.md) · [GitHub Pages](./site/README.md) · [라이선스](./LICENSE)

---

## 한눈에 보기

| 항목 | 내용 |
|------|------|
| 프로젝트명 | `radar_everything` |
| 목적 | 여러 소스의 “인기 / 스타 / 심각도” 신호를 기간별로 자동 수집 |
| 기본 소스 | GitHub, MCP Servers, 취약점(KISA 보호나라 + NVD) |
| 기간 | 주간(각 주) · 월간(각 월) · 연간 |
| 스택 | FastAPI · React(Vite) · SQLite · Docker Compose |
| 배포 | 단일 Docker 이미지 (프론트 빌드 포함) |
| 라이선스 | MIT |

---

## 왜 radar_everything 인가?

- **Everything**: GitHub만 보는 툴이 아니라, MCP·취약점 등 관심 신호를 같은 UX로 묶습니다.
- **Radar**: 주/월/연 타임라인에서 “지금 튀는 신호”를 빠르게 스캔합니다.
- **Extensible**: `BaseCollector` 하나 추가하면 UI·API·스케줄러에 자동으로 연결됩니다.
- **Clone & Run**: 복잡한 인프라 없이 Docker Compose로 즉시 기동합니다.

---

## 주요 기능

### 1) GitHub Radar
- 선택한 **주 / 월 / 년** 구간의 공개 저장소를 star 기준으로 랭킹
- GitHub Search API 우선, 실패 시 Trending HTML fallback
- 언어 · 토픽 · forks 등 메타데이터 포함

### 2) MCP Radar
- `mcp-server` / MCP 관련 저장소를 star 기준으로 수집
- 공식 MCP Registry 메타데이터로 결과 보강
- 주간·월간·연간 동일 UI로 탐색

### 3) Vulnerability Radar
- [보호나라(boho.or.kr)](https://www.boho.or.kr/) RSS (취약점 정보 · 보안공지)
- NVD CVE API로 **CVSS / 심각도** 보강
- Critical → High → Medium → Low 필터 및 정렬

### 4) 운영 기능
- 기동 시 자동 수집 (`COLLECT_ON_STARTUP`)
- 스케줄 수집 (기본 UTC 06:00, 18:00)
- UI에서 **지금 수집** 버튼으로 즉시 갱신
- REST API로 외부 자동화/연동 가능

---

## GitHub Pages

프로젝트 소개 랜딩 페이지는 `site/` 에 있으며, Actions로 Pages에 자동 배포됩니다.

1. 레포 **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. `main`(또는 `master`)에 push하면 `site/` 가 배포됩니다
3. URL 예: `https://<your-account>.github.io/radar_everything/`

> Pages는 **정적 소개 사이트**입니다. 실제 수집 웹앱(API·스케줄러)은 아래 Docker로 실행하세요.

로컬에서 랜딩만 미리보기:

```bash
# Python 3
cd site
python -m http.server 5500
# http://localhost:5500
```

---

## 60초 Quick Start

```bash
git clone https://github.com/<your-account>/radar_everything.git
cd radar_everything
cp .env.example .env
```

`.env`에 GitHub 토큰을 넣는 것을 권장합니다 (없어도 동작하지만 rate limit이 낮습니다).

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
# NVD_API_KEY=          # 선택
# PORT=8080
```

```bash
docker compose up --build -d
```

브라우저에서 **http://localhost:8080** 을 엽니다.

중지:

```bash
docker compose down
```

데이터 유지한 채 재시작:

```bash
docker compose up -d
```

---

## 화면 사용법 (요약)

1. 상단 소스 탭에서 **GitHub / MCP / 취약점** 선택  
2. **주간 · 월간 · 연간** 선택  
3. 세부 기간 칩에서 원하는 주(`2026-W47`) / 월(`2026-11`) / 년(`2026`) 선택  
4. 필요 시 검색어 · 심각도 필터 적용  
5. 데이터가 비어 있으면 **지금 수집** 클릭  

자세한 UI/운영 설명은 [docs/MANUAL.md](./docs/MANUAL.md)를 보세요.

---

## 로컬 개발 (Docker 없이)

### Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
set COLLECT_ON_STARTUP=false   # PowerShell: $env:COLLECT_ON_STARTUP='false'
uvicorn app.main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173 (`/api` → `localhost:8000` 프록시)

---

## API 요약

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/api/health` | 헬스체크 |
| `GET` | `/api/sources` | 등록된 소스 목록 |
| `GET` | `/api/periods/{source}/{period_type}` | 선택 가능한 기간 키 |
| `GET` | `/api/trends/{source}` | 랭킹 결과 |
| `POST` | `/api/collect?sync=true` | 즉시 수집 |
| `GET` | `/api/runs` | 수집 이력 |
| `GET` | `/api/stats` | 인덱스 통계 |

예시:

```bash
curl -X POST "http://localhost:8080/api/collect?sync=true" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"github\",\"period_type\":\"weekly\"}"
```

```bash
curl "http://localhost:8080/api/trends/github?period_type=weekly&period_key=2026-W47&limit=20"
```

전체 파라미터·응답 예시는 [매뉴얼 API 섹션](./docs/MANUAL.md#api-레퍼런스)을 참고하세요.

---

## 새 소스 추가 (플러그인)

1. `backend/app/collectors/my_source.py`에 `BaseCollector` 구현  
2. `backend/app/collectors/registry.py`에서 `register(MyCollector())`  
3. `.env`의 `ENABLED_SOURCES`에 `my_source` 추가  

템플릿: [`backend/app/collectors/example_plugin.py`](./backend/app/collectors/example_plugin.py)

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `GITHUB_TOKEN` | (empty) | GitHub API 인증 (권장) |
| `NVD_API_KEY` | (empty) | NVD CVE API 키 (선택) |
| `ENABLED_SOURCES` | `github,mcp,vulnerability` | 활성 소스 |
| `COLLECT_ON_STARTUP` | `true` | 컨테이너 기동 시 수집 |
| `COLLECT_CRON_HOURS` | `6,18` | 스케줄 시각 (UTC) |
| `DEFAULT_LIMIT` | `30` | 수집/표시 기본 개수 |
| `PORT` | `8080` | 호스트 포트 |
| `DATABASE_URL` | SQLite 파일 | DB 연결 문자열 |
| `CORS_ORIGINS` | localhost 목록 | CORS 허용 origin |

자세한 설명은 [매뉴얼 - 설정](./docs/MANUAL.md#설정환경-변수)을 보세요.

---

## 프로젝트 구조

```
radar_everything/
├── backend/
│   └── app/
│       ├── api/           # REST 라우트
│       ├── collectors/    # 소스 플러그인
│       ├── models/        # DB 모델
│       ├── services/      # 수집·조회·스케줄
│       └── core/          # 설정·DB
├── frontend/              # React UI (앱)
├── site/                  # GitHub Pages 랜딩
├── docs/
│   ├── MANUAL.md          # 사용자·운영 매뉴얼
│   └── GITHUB_LISTING.md  # GitHub description / About 문구
├── .github/workflows/
│   └── pages.yml          # Pages 자동 배포
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

---

## 한계와 주의

- GitHub은 “기간 동안 증가한 star” 공식 API가 없어, **기간 내 생성/활동 저장소의 star 랭킹**(+ Trending fallback)을 사용합니다.
- 비인증 GitHub API는 rate limit이 낮습니다. Public 배포·다수 수집 시 **Personal Access Token**을 권장합니다.
- NVD의 날짜 필터는 약 120일 제한이 있어, 연간 구간의 CVE는 창 끝부분 기준으로 조회합니다.
- 외부 사이트(보호나라 등) HTML/RSS 구조 변경 시 파서가 깨질 수 있습니다.
- 각 API/사이트의 ToS · rate limit을 준수하세요.

---

## 기여

이슈·PR 환영합니다.

1. fork → feature 브랜치  
2. 로컬에서 수집/UI 확인  
3. 작은 단위로 PR  

새 소스 추가 PR은 `example_plugin.py` 패턴을 따라 주세요.

---

## 관련 문서

- [사용자·운영 매뉴얼](./docs/MANUAL.md)
- [GitHub Description / Topics / About 문구](./docs/GITHUB_LISTING.md)
- [환경변수 예시](./.env.example)

---

## License

[MIT](./LICENSE)
