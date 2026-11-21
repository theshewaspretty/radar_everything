# GitHub 등록용 문구 모음 (radar_everything)

저장소 만들 때 **그대로 복사해 붙여 넣거나**, 톤만 바꿔 자유롭게 써도 됩니다.  
공식 고정 문구가 아니라 **재사용·변형 자유**인 카피 세트입니다.

---

## 1. Repository name

```
radar_everything
```

---

## 2. Description (About 옆 한 줄)

GitHub 저장소 **Description** 칸은 보통 짧은 영문/국문 한 줄입니다.  
아래에서 하나 고르거나 섞어 쓰세요. (권장 길이: 80자 전후)

### 추천 (영문 · 짧음)

```
Extensible radar for GitHub stars, MCP servers, and CVE/vuln trends — weekly, monthly, yearly. Docker one-liner.
```

### 추천 (국문 · 짧음)

```
GitHub·MCP·취약점 신호를 주간/월간/연간으로 자동 수집하는 확장형 레이더. Docker로 바로 실행.
```

### 대안 A — 제품 톤

```
Scan what’s trending across GitHub, MCP, and vulnerability feeds. Plug in new sources anytime.
```

### 대안 B — 개발자 톤

```
Plugin-based trend radar (FastAPI + React + SQLite). Clone, docker compose up, done.
```

### 대안 C — 보안/관측 톤

```
Open-source signal radar: popular repos, MCP servers, and KISA/NVD vulnerability severity over time.
```

### 대안 D — 초단문

```
Everything on your radar — stars, MCP, CVEs. Weekly · Monthly · Yearly.
```

---

## 3. Topics (GitHub Topics 태그)

About 패널의 **Topics**에 추가할 수 있는 태그 제안입니다.  
필요한 것만 골라 넣으세요.

```
radar
trend
github
stars
mcp
model-context-protocol
cve
cvss
vulnerability
kisa
security
fastapi
react
docker
docker-compose
sqlite
self-hosted
open-source
dashboard
osint
```

최소 세트:

```
radar, github, mcp, cve, docker, fastapi, react
```

---

## 4. Website / 홈페이지 필드

GitHub Pages를 켠 뒤 About → Website에 넣으세요.
(Settings → Pages → Folder는 **`/docs`** 로 설정. 데모는 `/app/` 경로.)

```
https://<your-account>.github.io/radar_everything/
```

데모 앱 직링크:

```
https://<your-account>.github.io/radar_everything/app/
```

Pages 전이라면 README 앵커도 가능합니다.

```
https://github.com/<your-account>/radar_everything#readme
```

커스텀 도메인을 쓰면:

```
https://<your-domain>
```

---

## 5. Social preview / README 상단 배지용 한 줄

```
radar_everything — put anything on the radar: GitHub · MCP · Vulnerabilities
```

국문:

```
radar_everything — GitHub·MCP·취약점, 무엇이든 레이더에
```

---

## 6. Release / 태그 노트용 짧은 소개

```
radar_everything v1.0.0

- Collect GitHub / MCP / vulnerability signals by week, month, and year
- Plugin architecture for new sources
- Single Docker image with UI + API
- MIT licensed, clone-and-run friendly
```

---

## 7. README 히어로 대체 카피 (자유 변형용)

### 버전 1 — 미션

```
세상의 신호를 한 레이더에.
GitHub 스타, MCP 인기, 취약점 심각도까지 — 주간·월간·연간으로 자동 스캔.
```

### 버전 2 — 실용

```
트렌드를 새로고침하지 말고, 레이더를 켜세요.
docker compose up 한 번이면 GitHub·MCP·CVE 랭킹이 로컬에 뜹니다.
```

### 버전 3 — 확장성

```
오늘은 GitHub과 CVE, 내일은 당신만의 소스.
BaseCollector 하나면 radar_everything에 새 신호가 붙습니다.
```

### 버전 4 — English pitch

```
One radar. Many signals.
Track stars, MCP servers, and vulnerability severity across weekly, monthly, and yearly windows — then plug in your own sources.
```

---

## 8. GitHub “About” 전체 채우기 예시

실제로 About 박스를 채울 때 예시:

| 필드 | 값 |
|------|----|
| Description | `Extensible radar for GitHub stars, MCP servers, and CVE/vuln trends — weekly, monthly, yearly. Docker one-liner.` |
| Website | `(배포 URL 또는 README)` |
| Topics | `radar`, `github`, `mcp`, `cve`, `docker`, `fastapi`, `react` |
| Releases | Public |
| Packages | 끄기 |
| Deployments | 선택 |

체크박스:

- [x] Releases  
- [ ] Packages  
- [ ] Deployments  

---

## 9. Issue / Discussion 템플릿용 안내 문구

```
Thanks for opening an issue on radar_everything!

Please include:
1) How you ran it (Docker / local)
2) Source tab (github / mcp / vulnerability)
3) Period (weekly/monthly/yearly + period_key)
4) Logs from `docker compose logs app` (redact tokens)
```

국문:

```
radar_everything 이슈를 남겨 주셔서 감사합니다.

다음을 알려 주세요.
1) 실행 방법 (Docker / 로컬)
2) 소스 탭
3) 기간 유형과 period_key
4) 로그 (토큰은 가려 주세요)
```

---

## 10. SNS / 쇼츠 / 커뮤니티 공유용

### 짧은 포스트 (KR)

```
radar_everything 오픈소스 공개 🛰️
GitHub 스타 · MCP · 취약점(CVE)을 주간/월간/연간으로 자동 수집.
Docker 한 줄로 로컬 실행, 소스도 플러그인으로 추가 가능.
#opensource #github #mcp #cve #docker
```

### 짧은 포스트 (EN)

```
Introducing radar_everything 🛰️
An extensible trend radar for GitHub stars, MCP servers, and CVE severity — weekly, monthly, yearly.
Clone → docker compose up → done.
```

### LinkedIn / 블로그 도입부

```
트렌드 페이지를 여러 개 열어두지 않아도 됩니다.
radar_everything은 GitHub, MCP, 취약점 피드를 하나의 타임라인 레이더로 모읍니다.
FastAPI + React + SQLite 기반이며, Docker Compose로 즉시 실행되고, 새 데이터 소스는 collector 플러그인으로 확장합니다.
```

---

## 11. 라이선스 / 인용 문구

```
radar_everything is released under the MIT License.
You are free to use, modify, and redistribute — commercially or privately — with attribution via the license notice.
```

국문:

```
radar_everything은 MIT 라이선스입니다.
라이선스 고지와 함께 사용·수정·재배포가 자유롭습니다.
```

---

## 12. “자유롭게 써도 된다” 가이드

이 파일의 문구는 전부 **재사용·편집·번역·혼합**해도 됩니다.

- GitHub Description / Topics / Release note
- 블로그, 포트폴리오, 발표 슬라이드
- README 히어로 문장 교체
- 데모 영상 자막

꼭 지킬 것:

1. 프로젝트명 표기는 **`radar_everything`** 권장  
2. 타 서비스 상표(GitHub, MCP, NVD, 보호나라 등)는 사실 관계에 맞게 언급  
3. 토큰·개인키는 공개 문구에 넣지 말 것  
4. MIT 라이선스 고지는 코드 배포 시 유지  

---

## 13. 한 장 요약 (복붙용)

```
radar_everything
Extensible open-source radar for GitHub stars, MCP servers, and vulnerability (KISA/NVD) trends.
Supports weekly / monthly / yearly views. Plugin collectors. FastAPI + React + SQLite. Docker Compose one-liner. MIT.
```

국문 한 장:

```
radar_everything
GitHub 스타 · MCP 서버 · 취약점(보호나라/CVE) 신호를 주간·월간·연간으로 모으는 확장형 오픈소스 레이더.
플러그인 컬렉터, FastAPI + React + SQLite, Docker Compose 원커맨드 실행. MIT.
```
