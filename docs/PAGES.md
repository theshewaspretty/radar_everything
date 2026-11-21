# GitHub Pages (`docs/`)

GitHub Pages는 브랜치 배포 시 **`/`(루트)** 또는 **`/docs`** 만 선택할 수 있습니다.  
(`site/` 같은 임의 폴더는 UI에서 고를 수 없습니다.)

그래서 랜딩 + 데모 앱을 **`docs/`** 아래에 둡니다.

| 경로 | 파일 | URL |
|------|------|-----|
| 랜딩 | `docs/index.html` | `https://<user>.github.io/<repo>/` |
| 데모 | `docs/app/` | `https://<user>.github.io/<repo>/app/` |
| 매뉴얼 등 | `docs/*.md` | (원하면 브라우저에서 raw/렌더로도 열림) |

---

## 설정 방법 (Deploy from a branch) — 권장·간단

1. 이 변경을 push  
2. 레포 **Settings → Pages**  
3. **Source: Deploy from a branch**  
4. Branch: `main` (또는 `master`)  
5. Folder: **`/docs`** ← 여기!  
6. Save  

수 분 후:

- `https://<user>.github.io/<repo>/`
- `https://<user>.github.io/<repo>/app/`

---

## 설정 방법 (GitHub Actions)

1. **Source: GitHub Actions**  
2. `.github/workflows/pages.yml` 실행 (push 또는 수동)  
3. Actions가 프론트 데모를 `docs/app/`에 빌드한 뒤 배포  

---

## 데모 앱

- UI: 소스 / 주·월·연 / 검색 / 심각도  
- 데이터: `docs/app/demo-data/snapshot.json` (빌드 시 `frontend/public/demo-data`에서 복사)  
- GitHub·MCP 「데모 수집」: 브라우저 → GitHub API  
- 취약점 라이브: CORS로 불가 → 샘플만  

풀스택은 Docker:

```bash
docker compose up --build -d
```

## 로컬에서 데모 다시 빌드해 docs에 넣기

```bash
cd frontend
set VITE_DEMO_MODE=true
set VITE_BASE=./
npm run build

# PowerShell
Remove-Item -Recurse -Force ..\docs\app -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path ..\docs\app | Out-Null
Copy-Item -Recurse -Force dist\* ..\docs\app\
Copy-Item -Force ..\docs\app\index.html ..\docs\app\404.html
```
