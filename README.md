# WestMonth Amazon US 选品云

内部生产级 Amazon US 选品平台，面向家居清洁 / 汽车用品方向，整合 WestMonth 货盘、Amazon US 前台线索、站外趋势、利润估算、风险审查、证据链和推荐动作。

## 已实现模块

- Next.js + React + Tailwind 工作台：Dashboard、批量搜索、详情报告、风险审查、趋势、设置、登录。
- FastAPI 后端：认证、权限、关键词分析、货盘导入、机会列表、风险列表、证据链、收藏备注、CSV / Excel 导出、同步任务入口。
- PostgreSQL schema：包含 `catalog_products`、`amazon_products`、`search_keywords`、`trend_snapshots`、`competitor_links`、`risk_assessments`、`profit_calculations`、`source_evidence`、`user_notes`、`saved_opportunities`、`sync_jobs` 等表。
- Skill 嵌入：后端 `WestMonthSkillAdapter` 会调用本机 `westmonth-catalog-analyzer` 的 `catalog_tool.py match`；分析逻辑按 `amazon-product-hunter` 的需求、利润、竞品、风险、货盘匹配流程实现。
- 数据真实性机制：每条来源保留来源名、链接、摘要、抓取时间和置信度；未启用实时数据源时默认标为 `low` 或 `待确认`。

## 项目结构

```text
westmonth-amazon-cloud/
  apps/
    api/                 FastAPI 后端
      app/
        adapters/        WestMonth、Amazon、趋势数据适配器
        api/routes/      API 路由
        models/          SQLAlchemy 数据模型
        services/        分析流水线与评分算法
        tasks/           定时任务入口
      scripts/seed_admin.py
      tests/
    web/                 Next.js 前端
      app/               页面路由
      components/        工作台组件
      lib/               API 客户端
  infra/migrations/      PostgreSQL 初始化 SQL
  packages/shared/       共享字段契约
  docker-compose.yml
```

## 本地启动

1. 复制环境变量：

```powershell
Copy-Item .env.example .env
```

2. 启动 PostgreSQL：

```powershell
docker compose up -d postgres
```

3. 启动后端：

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/seed_admin.py
uvicorn app.main:app --reload --port 8000
```

4. 启动前端：

```powershell
cd apps/web
npm install
npm run dev
```

5. 打开：

- 前端：http://localhost:3000
- 后端健康检查：http://localhost:8000/health
- 默认账号：`admin@westmonth.local`
- 默认密码：`ChangeMe123!`

首次上线前必须修改默认密码和 `JWT_SECRET`。

## 核心流程

1. 分析师在“搜索”页输入一个或多个关键词。
2. 后端创建 `search_keywords` 记录。
3. Amazon 适配器记录 Amazon US 搜索入口、竞品样本和低置信度证据。
4. 趋势适配器记录 Google Trends、TikTok / Reddit / 博客待验证入口。
5. WestMonth 适配器调用 `westmonth-catalog-analyzer` 做货盘匹配。
6. `OpportunityAnalyzer` 计算需求、利润、竞品、货盘匹配、风险。
7. 评分公式：

```text
Opportunity Score = Demand x Margin x Competition x Catalog Match x Risk Adjustment
Risk Adjustment = 1 - Risk Score / 120
```

8. 风险分高于 70 的产品标记为高风险并默认推荐“放弃”。
9. 结果进入 Dashboard、详情报告、风险审查和导出。

## 数据源扩展

当前 Amazon 和趋势适配器是合规占位实现，保留证据链接和低置信度标记，方便上线前替换为正式数据源：

- Amazon：Amazon PA-API、Keepa、DataHawk、Rainforest API、合规自建采集。
- Google Trends：pytrends 或托管趋势 API。
- TikTok：TikTok Creative Center 或授权第三方趋势 API。
- Reddit / 博客：Reddit API、Firecrawl、SerpAPI、RSS / 媒体数据库。
- 风险：USPTO TESS / Patent Center、Amazon restricted products、CPSC / FDA / FCC / UL 数据源。

新增数据源只需要继承 `SourceAdapter`，返回结构化数据和 `source_evidence`。

## 云端部署建议

- Web：Vercel，设置 `NEXT_PUBLIC_API_BASE` 指向后端域名。
- API：Render / Railway，使用 `apps/api/Dockerfile`。
- DB：Supabase PostgreSQL 或 Railway PostgreSQL，执行 `infra/migrations/001_initial_schema.sql`。
- 定时任务：Render Cron / Railway Cron / GitHub Actions 调用 `/api/v1/jobs/schedule`，或把 `tasks/scheduler.py` 扩展成常驻 worker。
- Secrets：`DATABASE_URL`、`JWT_SECRET`、`OPENAI_API_KEY`、正式数据源 API Key。

## 后续扩展

- Listing 生成器：基于机会详情、竞品痛点和 WestMonth SKU 生成标题、五点、A+结构和图片需求。
- 批量上架：连接 Amazon SP-API，先走人工审批，再生成草稿 Listing。
- 真实利润模型：接入 FBA Fee API、尺寸重量、入仓运费、PPC ACOS 区间。
- 审核工作流：法务 / 运营 / 采购多角色状态流转。
- 数据质量：每个字段增加 `confidence`、`verified_by`、`verified_at`，并强制来源不足时进入“继续研究”。
