 # **radar_everything** 

<p align="center">

An extensible radar for GitHub stars, MCP servers, and CVE/vulnerability trends.

Weekly · Monthly · Yearly · Docker One-Liner

![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white) ![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Live Demo · Documentation · GitHub Repository

</p>

<p align="center">

🌐 Language / 语言 / 언어

English · 简体中文 · 한국어

</p>

English
Discover What's Trending. Track What Matters.

radar_everything is an extensible, self-hosted intelligence radar that collects, aggregates, and ranks signals from multiple external sources.

Track GitHub repositories, trending MCP servers, CVEs, and security advisories through weekly, monthly, and yearly timelines — all from one unified dashboard.

Run the complete application with Docker Compose, or explore the public GitHub Pages demo without installing anything.

✨ Key Features
GitHub Radar — Discover trending repositories based on stars and repository metadata.
MCP Radar — Track popular Model Context Protocol (MCP) servers and related projects.
Vulnerability Radar — Monitor CVEs, CVSS scores, and security advisories from NVD and KISA's BohoNara.
Time-based Rankings — Explore weekly, monthly, and yearly trends.
Extensible Collectors — Add new data sources through the BaseCollector plugin interface.
Automated Collection — Run scheduled data collection with configurable intervals.
Interactive Dashboard — Search, filter, and explore collected intelligence.
Docker Deployment — Launch the full-stack application with a single command.
GitHub Pages Demo — Try the frontend without deploying a backend.
🚀 Quick Start
Option 1: Docker Compose (Recommended)

Requirements:

Docker
Docker Compose

Clone the repository:

bash
git clone https://github.com/theshewaspretty/radar_everything.git
cd radar_everything


Configure environment variables:

bash
cp .env.example .env


Optionally configure API credentials:

env
GITHUB_TOKEN=your_github_token
NVD_API_KEY=
PORT=8080


Start the application:

bash
docker compose up --build -d


Open:

http://localhost:8080

Manage the application:

bash
# View logs
docker compose logs -f app

# Stop services
docker compose down

# Restart without removing stored data
docker compose up -d

# Rebuild
docker compose up --build -d


A GitHub token is recommended to increase API rate limits. The application can also run without one.

Option 2: GitHub Pages Demo

Try the application directly in your browser:

https://theshewaspretty.github.io/radar_everything/app/

The demo provides:

Interactive dashboard
Weekly, monthly, and yearly navigation
Sample ranking data
GitHub and MCP browser-based live queries (optional)
Search and filtering

No Docker installation or backend deployment is required.

Note: The Pages demo does not include the backend scheduler, SQLite database, or live KISA/NVD collection pipeline.

📡 Data Sources
1. GitHub Radar

Discover popular public GitHub repositories.

Repository star rankings
Programming language metadata
Repository topics
GitHub Search API
Trending HTML fallback
2. MCP Radar

Explore the MCP ecosystem.

MCP-related repositories
mcp-server discovery
Repository star rankings
Official MCP Registry metadata enrichment
3. Vulnerability Radar

Monitor security intelligence and vulnerability trends.

KISA BohoNara security advisories and RSS feeds
NVD CVE API vulnerability data
CVE identifiers
CVSS scores
Severity classification

Severity levels:

Severity	Description
Critical	Critical risk
High	High risk
Medium	Moderate risk
Low	Low risk
Info	Informational
📊 Time-based Intelligence

Explore collected intelligence through three time dimensions.

Period	Description	Example
Weekly	Weekly trends	2026-W47
Monthly	Monthly trends	2026-11
Yearly	Annual trends	2026

Use the dashboard to switch between periods, compare rankings, search entries, and filter vulnerability severity.

Important: GitHub does not provide an official historical star-growth ranking API. This project uses repository creation/activity windows and available Trending data as ranking signals rather than claiming exact historical star increments.

🧩 Extensible Collector Architecture

Add new intelligence sources without changing the core application.

Collector integration steps:

Create a collector in backend/app/collectors/.
Implement the BaseCollector interface.
Register the collector in registry.py.
Add its identifier to ENABLED_SOURCES.

Example:

python
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    source_id = "my_source"

    async def collect(self, period_type, period_key):
        # Implement your data collection logic
        return []


See:

backend/app/collectors/example_plugin.py

🖥️ Deployment Modes
Feature	Docker Full Stack	GitHub Pages Demo
Frontend UI	✅	✅
Sample data	Collected on startup	✅
GitHub live queries	Server-side	Browser-side
MCP live queries	Server-side	Browser-side
KISA/NVD live collection	✅	❌
SQLite database	✅	❌
Scheduled collection	✅	❌
REST API	✅	❌
Best for	Local/self-hosted usage	Public preview
🛠️ Local Development
Backend
bash
cd backend

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt


Disable startup collection during development:

bash
# Linux / macOS
export COLLECT_ON_STARTUP=false

# Windows PowerShell
$env:COLLECT_ON_STARTUP="false"


Start FastAPI:

bash
uvicorn app.main:app --reload --port 8000


API documentation:

http://localhost:8000/docs

Frontend
bash
cd frontend
npm install
npm run dev


Open:

http://localhost:5173

The development server proxies /api requests to the backend.

Demo Mode
bash
cd frontend
npm install
npm run dev:demo


This runs the frontend in the same demo mode used by GitHub Pages.

🔌 API Reference

Base URL:

text
http://localhost:8080/api

Method	Endpoint	Description
GET	/health	Health check
GET	/sources	List available sources
GET	/periods/{source}/{period_type}	List available periods
GET	/trends/{source}	Retrieve rankings
POST	/collect	Trigger data collection
GET	/runs	Collection history
GET	/stats	Collection statistics

Example: Trigger GitHub collection.

bash
curl -X POST "http://localhost:8080/api/collect?sync=true" \
  -H "Content-Type: application/json" \
  -d '{"source":"github","period_type":"weekly"}'


Example: Retrieve weekly GitHub rankings.

bash
curl "http://localhost:8080/api/trends/github?period_type=weekly&period_key=2026-W47&limit=20"


For complete API documentation, visit:

http://localhost:8000/docs

The GitHub Pages demo uses its local demo client and snapshot data instead of the backend API.

⚙️ Environment Variables
Variable	Default	Description
GITHUB_TOKEN	Empty	GitHub API authentication
NVD_API_KEY	Empty	NVD API key
ENABLED_SOURCES	github,mcp,vulnerability	Enabled collectors
COLLECT_ON_STARTUP	true	Collect data at startup
COLLECT_CRON_HOURS	6,18	Collection schedule (UTC)
DEFAULT_LIMIT	30	Default result limit
PORT	8080	Application port
DATABASE_URL	SQLite	Database connection
CORS_ORIGINS	localhost defaults	Allowed origins
APP_NAME	radar_everything	Application name

Frontend demo build variables:

Variable	Description
VITE_DEMO_MODE	Enable demo mode
VITE_BASE	GitHub Pages base path, e.g. /<repo>/app/

See .env.example and MANUAL.md for details.

📁 Project Structure
text
radar_everything/
├── backend/
│   └── app/
│       ├── api/              # REST API
│       ├── collectors/       # Data source plugins
│       ├── models/           # Database models
│       ├── services/         # Collection and scheduling
│       └── core/             # Application configuration
│
├── frontend/
│   ├── public/demo-data/     # Demo snapshot
│   └── src/
│       └── api/demo.ts       # Demo API client
│
├── docs/
│   ├── index.html            # Landing page
│   ├── app/                  # GitHub Pages demo
│   ├── MANUAL.md
│   ├── PAGES.md
│   └── GITHUB_LISTING.md
│
├── .github/workflows/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── LICENSE
└── README.md

🌐 GitHub Pages Configuration

GitHub Pages supports publishing from the repository root or /docs when using branch deployment.

This project keeps its landing page and demo application under docs/.

To enable:

Push your changes to GitHub.
Open Settings → Pages.
Select Deploy from a branch.
Choose branch master or your configured default branch.
Select folder /docs.
Save.

Access:

Landing page: https://theshewaspretty.github.io/radar_everything/
Demo application: https://theshewaspretty.github.io/radar_everything/app/

Alternatively, use the GitHub Actions deployment workflow:

.github/workflows/pages.yml

⚠️ Limitations & Notes
GitHub does not expose an official API for exact historical star increments. Rankings use available repository activity and Trending signals.
Unauthenticated GitHub API access has relatively low rate limits. A token is recommended for regular collection.
NVD date filtering has query-window limitations. Yearly CVE results may not represent a complete calendar year.
KISA RSS and HTML structures may change, requiring collector maintenance.
GitHub Pages is a public demonstration and does not replace the full backend collection pipeline.
External APIs and websites may impose rate limits and terms of service. Respect their policies.
🤝 Contributing

Contributions are welcome!

Fork the repository.
Create a feature branch.
Implement your changes.
Test using Docker or local development mode.
Submit a pull request.

New data sources should follow the example_plugin.py pattern.

📚 Documentation
Document	Description
MANUAL.md	Installation, UI, API, and troubleshooting
GITHUB_LISTING.md	GitHub description, topics, and promotion
PAGES.md	GitHub Pages deployment
.env.example	Environment configuration
📄 License

This project is licensed under the MIT License.

简体中文
发现趋势，追踪重要信号

radar_everything 是一个可扩展、自托管的情报雷达平台，用于自动收集、聚合和排名来自多个外部数据源的信息。

通过统一的仪表板，按周、月、年追踪 GitHub 开源项目、热门 MCP Server、CVE 漏洞和安全公告。

支持通过 Docker Compose 快速部署，也可以直接通过 GitHub Pages 在线体验，无需安装任何软件。

✨ 核心功能
GitHub Radar — 根据 Star 数量及仓库元数据发现热门开源项目。
MCP Radar — 追踪热门 Model Context Protocol（MCP）服务器及相关项目。
Vulnerability Radar — 监控 CVE、CVSS 评分，以及 NVD 和韩国 KISA BohoNara 的安全公告。
时间趋势分析 — 支持周、月、年三个时间维度。
可扩展采集器 — 通过 BaseCollector 插件接口添加新的数据源。
自动化数据采集 — 支持定时任务和可配置的采集周期。
交互式仪表板 — 搜索、筛选和查看采集结果。
Docker 部署 — 使用一条命令启动完整应用。
GitHub Pages 在线演示 — 无需部署后端即可体验前端界面。
🚀 快速开始
方式一：Docker Compose（推荐）

环境要求：

Docker
Docker Compose

克隆仓库：

bash
git clone https://github.com/theshewaspretty/radar_everything.git
cd radar_everything


复制环境变量配置：

bash
cp .env.example .env


根据需要配置 API 凭据：

env
GITHUB_TOKEN=your_github_token
NVD_API_KEY=
PORT=8080


启动应用：

bash
docker compose up --build -d


访问：

http://localhost:8080

常用管理命令：

bash
# 查看日志
docker compose logs -f app

# 停止服务
docker compose down

# 保留数据并重新启动
docker compose up -d

# 重新构建
docker compose up --build -d


建议配置 GitHub Token，以提高 API 请求速率限制。没有 Token 也可以运行。

方式二：GitHub Pages 在线演示

直接在浏览器中体验：

https://theshewaspretty.github.io/radar_everything/app/

演示功能包括：

交互式仪表板
周、月、年时间导航
示例排名数据
GitHub 和 MCP 浏览器端实时查询（可选）
搜索和筛选

无需安装 Docker，也无需部署后端。

注意：Pages 演示不包含后端调度器、SQLite 数据库，以及 KISA/NVD 实时数据采集流程。

📡 数据来源
1. GitHub Radar

发现热门公开 GitHub 仓库。

仓库 Star 排名
编程语言信息
仓库 Topics
GitHub Search API
Trending HTML 备用方案
2. MCP Radar

探索 MCP 生态系统。

MCP 相关仓库
mcp-server 项目发现
仓库 Star 排名
官方 MCP Registry 元数据补充
3. Vulnerability Radar

追踪安全情报和漏洞趋势。

KISA BohoNara 安全公告及 RSS
NVD CVE API 漏洞数据
CVE 编号
CVSS 评分
漏洞严重程度分类

严重程度：

级别	说明
Critical	严重
High	高危
Medium	中危
Low	低危
Info	信息
📊 时间趋势分析

支持三个时间维度：

周期	说明	示例
Weekly	每周趋势	2026-W47
Monthly	每月趋势	2026-11
Yearly	每年趋势	2026

可以切换时间范围、比较排名、搜索数据，以及筛选漏洞严重程度。

重要说明： GitHub 没有提供用于精确查询历史 Star 增量的官方 API。本项目使用仓库创建时间、活动时间范围及可用的 Trending 数据作为排名信号，并不声称提供精确的历史 Star 增长量。

🧩 可扩展采集器架构

无需修改核心应用即可添加新的情报数据源。

添加步骤：

在 backend/app/collectors/ 创建新的采集器。
实现 BaseCollector 接口。
在 registry.py 中注册采集器。
在 ENABLED_SOURCES 中添加对应 ID。

示例：

python
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    source_id = "my_source"

    async def collect(self, period_type, period_key):
        # 在此实现数据采集逻辑
        return []


参考：

backend/app/collectors/example_plugin.py

🖥️ 部署方式
功能	Docker 完整版	GitHub Pages 演示
前端 UI	✅	✅
示例数据	启动时采集	✅
GitHub 实时查询	服务端	浏览器端
MCP 实时查询	服务端	浏览器端
KISA/NVD 实时采集	✅	❌
SQLite 数据库	✅	❌
定时采集	✅	❌
REST API	✅	❌
适用场景	本地及自托管部署	在线体验
🛠️ 本地开发
Backend
bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt


开发时关闭启动自动采集：

bash
# Linux / macOS
export COLLECT_ON_STARTUP=false

# Windows PowerShell
$env:COLLECT_ON_STARTUP="false"


启动 FastAPI：

bash
uvicorn app.main:app --reload --port 8000


API 文档：

http://localhost:8000/docs

Frontend
bash
cd frontend
npm install
npm run dev


访问：

http://localhost:5173

开发服务器会将 /api 请求代理到后端。

Demo 模式
bash
cd frontend
npm install
npm run dev:demo


该模式与 GitHub Pages 演示使用相同的前端运行方式。

🔌 API 参考

基础地址：

text
http://localhost:8080/api

方法	接口	说明
GET	/health	健康检查
GET	/sources	数据源列表
GET	/periods/{source}/{period_type}	可用时间范围
GET	/trends/{source}	获取排名
POST	/collect	触发数据采集
GET	/runs	采集历史
GET	/stats	采集统计

触发 GitHub 周度采集：

bash
curl -X POST "http://localhost:8080/api/collect?sync=true" \
  -H "Content-Type: application/json" \
  -d '{"source":"github","period_type":"weekly"}'


查询 GitHub 周度排名：

bash
curl "http://localhost:8080/api/trends/github?period_type=weekly&period_key=2026-W47&limit=20"


完整 API 文档：

http://localhost:8000/docs

GitHub Pages 演示使用本地 Demo Client 和 Snapshot 数据，不依赖后端 API。

⚙️ 环境变量
变量	默认值	说明
GITHUB_TOKEN	空	GitHub API 认证
NVD_API_KEY	空	NVD API Key
ENABLED_SOURCES	github,mcp,vulnerability	启用的数据源
COLLECT_ON_STARTUP	true	启动时自动采集
COLLECT_CRON_HOURS	6,18	采集时间（UTC）
DEFAULT_LIMIT	30	默认结果数量
PORT	8080	应用端口
DATABASE_URL	SQLite	数据库连接
CORS_ORIGINS	localhost 默认值	允许的跨域来源
APP_NAME	radar_everything	应用名称

前端 Demo 构建变量：

变量	说明
VITE_DEMO_MODE	启用 Demo 模式
VITE_BASE	GitHub Pages 基础路径，例如 /<repo>/app/

详细配置请参考 .env.example 和 MANUAL.md。

📁 项目结构
text
radar_everything/
├── backend/
│   └── app/
│       ├── api/              # REST API
│       ├── collectors/       # 数据源插件
│       ├── models/           # 数据库模型
│       ├── services/         # 数据采集与调度
│       └── core/             # 核心配置
│
├── frontend/
│   ├── public/demo-data/     # Demo 快照
│   └── src/
│       └── api/demo.ts       # Demo API Client
│
├── docs/
│   ├── index.html            # 项目介绍页
│   ├── app/                  # GitHub Pages 演示
│   ├── MANUAL.md
│   ├── PAGES.md
│   └── GITHUB_LISTING.md
│
├── .github/workflows/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── LICENSE
└── README.md

🌐 GitHub Pages 配置

使用分支部署时，GitHub Pages 支持从仓库根目录 / 或 /docs 发布。

本项目将介绍页面和 Demo 应用放在 docs/ 目录中。

启用步骤：

将代码推送到 GitHub。
打开 Settings → Pages。
选择 Deploy from a branch。
选择 master 或实际使用的默认分支。
选择 /docs。
保存设置。

访问地址：

项目介绍：https://theshewaspretty.github.io/radar_everything/
在线演示：https://theshewaspretty.github.io/radar_everything/app/

也可以使用 GitHub Actions 部署：

.github/workflows/pages.yml

⚠️ 限制与注意事项
GitHub 没有提供精确查询历史 Star 增量的官方 API，因此排名基于可用的仓库活动及 Trending 信号。
未认证的 GitHub API 请求速率限制较低，建议配置 Token。
NVD 日期筛选存在查询窗口限制，年度 CVE 数据可能不覆盖完整自然年。
KISA RSS 和 HTML 页面结构发生变化时，可能需要更新解析器。
GitHub Pages 仅用于公开演示，不能替代完整后端采集流程。
使用外部 API 和网站时，请遵守各自的服务条款和速率限制。
🤝 参与贡献

欢迎提交贡献！

Fork 仓库。
创建功能分支。
实现修改。
使用 Docker 或本地开发模式测试。
提交 Pull Request。

新数据源请遵循 example_plugin.py 的实现方式。

📚 相关文档
文档	说明
MANUAL.md	安装、UI、API 和故障排查
GITHUB_LISTING.md	GitHub 简介、Topics 和推广文案
PAGES.md	GitHub Pages 部署
.env.example	环境变量配置
📄 许可证

本项目采用 MIT License。

한국어
무엇이든 레이더에 올려라.

radar_everything은 다양한 외부 데이터 소스를 자동으로 수집하고 통합하여 순위와 트렌드를 분석하는 확장형 오픈소스 인텔리전스 레이더 플랫폼입니다.

GitHub 오픈소스 프로젝트, 인기 MCP 서버, CVE 취약점 및 보안 공지를 하나의 대시보드에서 확인할 수 있습니다.

주간 · 월간 · 연간 단위로 데이터를 수집하고 분석하며, Docker Compose를 통해 간단하게 실행할 수 있습니다.

별도 설치 없이 GitHub Pages 데모를 통해서도 체험할 수 있습니다.

✨ 주요 기능
GitHub Radar — GitHub 공개 저장소의 Star 및 메타데이터 기반 인기 프로젝트 분석
MCP Radar — 인기 Model Context Protocol(MCP) 서버 및 관련 프로젝트 추적
Vulnerability Radar — CVE, CVSS 및 NVD, KISA 보호나라 보안 공지 모니터링
기간별 트렌드 — 주간, 월간, 연간 데이터 분석
확장형 Collector — BaseCollector 플러그인으로 새로운 데이터 소스 추가
자동 수집 — 스케줄러를 통한 주기적 데이터 수집
인터랙티브 대시보드 — 검색, 필터링 및 데이터 분석
Docker 배포 — 명령어 한 줄로 전체 애플리케이션 실행
GitHub Pages 데모 — 백엔드 설치 없이 웹에서 체험
🚀 빠른 시작
방법 1: Docker Compose (추천)

필요 환경:

Docker
Docker Compose

저장소 복제:

bash
git clone https://github.com/theshewaspretty/radar_everything.git
cd radar_everything


환경변수 파일 생성:

bash
cp .env.example .env


필요에 따라 API 인증 정보를 설정합니다.

env
GITHUB_TOKEN=your_github_token
NVD_API_KEY=
PORT=8080


애플리케이션 실행:

bash
docker compose up --build -d


접속:

http://localhost:8080

주요 관리 명령:

bash
# 로그 확인
docker compose logs -f app

# 서비스 중지
docker compose down

# 데이터 유지 후 재시작
docker compose up -d

# 이미지 재빌드
docker compose up --build -d


GitHub API 사용량 제한을 높이기 위해 GitHub Token 설정을 권장합니다. Token 없이도 실행할 수 있습니다.

방법 2: GitHub Pages 온라인 데모

브라우저에서 바로 체험할 수 있습니다.

https://theshewaspretty.github.io/radar_everything/app/

데모 기능:

인터랙티브 대시보드
주간 / 월간 / 연간 기간 탐색
샘플 랭킹 데이터
GitHub 및 MCP 브라우저 기반 라이브 조회(선택)
검색 및 필터링

Docker 설치나 Backend 배포가 필요하지 않습니다.

참고: Pages 데모는 Backend Scheduler, SQLite 데이터베이스, KISA/NVD 실시간 수집 파이프라인을 포함하지 않습니다.

📡 데이터 수집 소스
1. GitHub Radar

인기 있는 공개 GitHub 저장소를 탐색합니다.

저장소 Star 순위
프로그래밍 언어 정보
저장소 Topics
GitHub Search API
Trending HTML 대체 수집 방식
2. MCP Radar

MCP 생태계의 트렌드를 추적합니다.

MCP 관련 저장소
mcp-server 프로젝트 탐색
저장소 Star 순위
공식 MCP Registry 메타데이터 보강
3. Vulnerability Radar

보안 인텔리전스 및 취약점 트렌드를 모니터링합니다.

KISA 보호나라 보안 공지 및 RSS
NVD CVE API 취약점 정보
CVE 식별자
CVSS 점수
취약점 심각도 분류

심각도 분류:

등급	설명
Critical	치명적
High	높음
Medium	중간
Low	낮음
Info	정보
📊 기간별 트렌드 분석

다음 세 가지 기간을 지원합니다.

기간	설명	예시
Weekly	주간 트렌드	2026-W47
Monthly	월간 트렌드	2026-11
Yearly	연간 트렌드	2026

대시보드에서 기간을 전환하고 순위를 비교하거나 검색할 수 있으며, 취약점 심각도별 필터링도 가능합니다.

중요: GitHub는 과거 특정 기간의 정확한 Star 증가량을 제공하는 공식 API를 지원하지 않습니다. 본 프로젝트는 저장소 생성 및 활동 기간과 사용 가능한 Trending 데이터를 랭킹 신호로 사용하며, 정확한 과거 Star 증가량을 제공한다고 주장하지 않습니다.

🧩 확장 가능한 Collector 아키텍처

핵심 애플리케이션을 수정하지 않고 새로운 데이터 소스를 추가할 수 있습니다.

추가 방법:

backend/app/collectors/에 Collector를 생성합니다.
BaseCollector 인터페이스를 구현합니다.
registry.py에서 Collector를 등록합니다.
ENABLED_SOURCES에 해당 ID를 추가합니다.

예시:

python
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    source_id = "my_source"

    async def collect(self, period_type, period_key):
        # 데이터 수집 로직 구현
        return []


참고:

backend/app/collectors/example_plugin.py

🖥️ 실행 방식 비교
기능	Docker 풀스택	GitHub Pages 데모
Frontend UI	✅	✅
샘플 데이터	실행 시 수집	✅
GitHub 라이브 조회	서버	브라우저
MCP 라이브 조회	서버	브라우저
KISA/NVD 라이브 수집	✅	❌
SQLite 데이터베이스	✅	❌
스케줄러	✅	❌
REST API	✅	❌
주요 용도	로컬 및 자체 서버 운영	공개 데모
🛠️ 로컬 개발 환경
Backend
bash
cd backend

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt


개발 환경에서는 시작 시 자동 수집을 비활성화합니다.

bash
# Linux / macOS
export COLLECT_ON_STARTUP=false

# Windows PowerShell
$env:COLLECT_ON_STARTUP="false"


FastAPI 실행:

bash
uvicorn app.main:app --reload --port 8000


API 문서:

http://localhost:8000/docs

Frontend
bash
cd frontend
npm install
npm run dev


접속:

http://localhost:5173

개발 서버는 /api 요청을 Backend로 프록시합니다.

Demo 모드
bash
cd frontend
npm install
npm run dev:demo


GitHub Pages와 동일한 Demo 모드로 실행합니다.

🔌 API 레퍼런스

기본 주소:

text
http://localhost:8080/api

Method	Endpoint	설명
GET	/health	헬스체크
GET	/sources	데이터 소스 목록
GET	/periods/{source}/{period_type}	사용 가능한 기간 목록
GET	/trends/{source}	랭킹 조회
POST	/collect	데이터 수집 실행
GET	/runs	수집 이력
GET	/stats	수집 통계

GitHub 주간 데이터 수집:

bash
curl -X POST "http://localhost:8080/api/collect?sync=true" \
  -H "Content-Type: application/json" \
  -d '{"source":"github","period_type":"weekly"}'


GitHub 주간 랭킹 조회:

bash
curl "http://localhost:8080/api/trends/github?period_type=weekly&period_key=2026-W47&limit=20"


전체 API 문서:

http://localhost:8000/docs

GitHub Pages 데모는 Backend API 대신 로컬 Demo Client와 Snapshot 데이터를 사용합니다.

⚙️ 환경변수
변수	기본값	설명
GITHUB_TOKEN	비어 있음	GitHub API 인증
NVD_API_KEY	비어 있음	NVD API Key
ENABLED_SOURCES	github,mcp,vulnerability	활성화할 Collector
COLLECT_ON_STARTUP	true	시작 시 자동 수집
COLLECT_CRON_HOURS	6,18	수집 시간 (UTC)
DEFAULT_LIMIT	30	기본 결과 개수
PORT	8080	애플리케이션 포트
DATABASE_URL	SQLite	데이터베이스 연결
CORS_ORIGINS	localhost 기본값	허용할 Origin
APP_NAME	radar_everything	애플리케이션 이름

Frontend Demo 빌드 변수:

변수	설명
VITE_DEMO_MODE	Demo 모드 활성화
VITE_BASE	GitHub Pages 기본 경로 (예: /<repo>/app/)

자세한 내용은 .env.example 및 MANUAL.md를 참고하세요.

📁 프로젝트 디렉터리 구조
text
radar_everything/
├── backend/
│   └── app/
│       ├── api/              # REST API
│       ├── collectors/       # 데이터 소스 플러그인
│       ├── models/           # 데이터베이스 모델
│       ├── services/         # 수집 및 스케줄 관리
│       └── core/             # 애플리케이션 설정
│
├── frontend/
│   ├── public/demo-data/     # Demo Snapshot
│   └── src/
│       └── api/demo.ts       # Demo API Client
│
├── docs/
│   ├── index.html            # 프로젝트 소개 페이지
│   ├── app/                  # GitHub Pages 데모
│   ├── MANUAL.md
│   ├── PAGES.md
│   └── GITHUB_LISTING.md
│
├── .github/workflows/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── LICENSE
└── README.md

🌐 GitHub Pages 설정

GitHub Pages의 브랜치 배포는 저장소 루트 / 또는 /docs를 사용할 수 있습니다.

본 프로젝트는 소개 페이지와 Demo 앱을 docs/ 디렉터리에 구성합니다.

설정 방법:

변경 사항을 GitHub에 Push합니다.
Settings → Pages로 이동합니다.
Deploy from a branch를 선택합니다.
master 또는 실제 기본 브랜치를 선택합니다.
폴더 /docs를 선택합니다.
저장합니다.

접속 주소:

프로젝트 소개: https://theshewaspretty.github.io/radar_everything/
온라인 데모: https://theshewaspretty.github.io/radar_everything/app/

GitHub Actions를 통한 배포도 지원합니다.

.github/workflows/pages.yml

⚠️ 제한 사항 및 참고
GitHub는 과거 특정 기간의 정확한 Star 증가량을 제공하는 공식 API가 없습니다. 따라서 사용 가능한 저장소 활동 및 Trending 신호를 기반으로 랭킹을 계산합니다.
인증되지 않은 GitHub API 요청은 사용량 제한이 낮으므로 Token 사용을 권장합니다.
NVD 날짜 필터에는 조회 기간 제한이 있으며, 연간 CVE 결과가 완전한 1년 데이터를 포함하지 않을 수 있습니다.
KISA RSS 및 HTML 구조 변경 시 Collector 수정이 필요할 수 있습니다.
GitHub Pages는 공개 데모용이며 전체 Backend 수집 파이프라인을 대체하지 않습니다.
외부 API 및 웹사이트의 이용 약관과 요청 제한을 준수해야 합니다.
🤝 기여하기

프로젝트 기여를 환영합니다!

저장소를 Fork합니다.
Feature 브랜치를 생성합니다.
기능을 구현합니다.
Docker 또는 로컬 개발 환경에서 테스트합니다.
Pull Request를 제출합니다.

새로운 데이터 소스는 example_plugin.py 구현 패턴을 따라 주세요.

📚 관련 문서
문서	설명
MANUAL.md	설치, UI, API 및 문제 해결
GITHUB_LISTING.md	GitHub 소개, Topics 및 홍보 문구
PAGES.md	GitHub Pages 배포
.env.example	환경변수 예시
📄 라이선스

본 프로젝트는 MIT License를 따릅니다.

<p align="center">

radar_everything

Discover trends. Track signals. Build your own radar.

GitHub · Live Demo

</p>
