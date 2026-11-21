# GitHub Pages (`site/`)

`radar_everything` 프로젝트 사이트 + **데모 앱** 배포 폴더입니다.

| 경로 | 내용 |
|------|------|
| `/` (`site/index.html`) | 소개 랜딩 |
| `/app/` (`site/app/` ← CI가 빌드) | 실제 UI 데모 (정적) |

예상 URL:

```
https://<user>.github.io/radar_everything/
https://<user>.github.io/radar_everything/app/
```

## 데모 앱이 하는 일

- React UI 전체 (소스/주월연/검색/심각도)
- `demo-data/snapshot.json` 샘플 랭킹
- **지금 수집(데모 수집)**
  - GitHub / MCP: 브라우저에서 GitHub Search API 직접 호출 (세션에 저장)
  - 취약점: CORS 때문에 샘플 데이터 갱신

## 데모가 못 하는 일

- 서버 스케줄러 / SQLite 영속화
- 보호나라 RSS · NVD 서버 측 수집
- 비인증 GitHub API rate limit 공유 (방문자가 많으면 429 가능)

풀기능은 루트에서:

```bash
docker compose up --build -d
```

## 로컬에서 데모 미리보기

```bash
cd frontend
# base를 / 로 두고 싶을 때
set VITE_DEMO_MODE=true
set VITE_BASE=/
npm run build
npx vite preview
```

또는:

```bash
npm run dev:demo
```

(`frontend/.env.demo` 사용 — Pages용 base 경로 포함)

## CI

`.github/workflows/pages.yml` 이 frontend를 `VITE_DEMO_MODE=true` 로 빌드해 `site/app/` 에 넣고 Pages로 배포합니다.
