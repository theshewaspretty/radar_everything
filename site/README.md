# GitHub Pages (`site/`)

`radar_everything` 프로젝트 소개용 **정적 랜딩 사이트**입니다.

| 항목 | 내용 |
|------|------|
| 배포 경로 | 이 폴더 전체 (`index.html`, `assets/`, `404.html`) |
| 자동화 | `.github/workflows/pages.yml` |
| 예상 URL | `https://<user>.github.io/radar_everything/` |

## 활성화

1. GitHub 저장소 **Settings → Pages**
2. Source: **GitHub Actions**
3. `main`/`master` push 또는 workflow_dispatch

## 로컬 미리보기

```bash
cd site
python -m http.server 5500
```

## 앱과의 관계

- **Pages (`site/`)** = 마케팅/문서 랜딩 (정적)
- **Docker 앱 (`frontend/` + `backend/`)** = 실제 수집·랭킹 웹서비스

Pages만으로는 GitHub/MCP/취약점 수집이 동작하지 않습니다.
