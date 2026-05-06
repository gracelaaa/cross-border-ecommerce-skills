# Cross-Border E-Commerce AI Skills

**40 AI-powered skill templates for cross-border e-commerce — from brand strategy to Amazon operations to DTC growth to overseas-buyer prospecting + earned-media press discovery.**

Compatible with Claude Code (`~/.claude/commands/`), Google Antigravity (`SKILL.md`), and any AI IDE with skill/prompt support.

[中文说明](#中文说明) | [English](#english)

---

## English

### What is this?

A collection of **40 AI agent skills** (structured prompt templates) that automate the entire cross-border e-commerce workflow — brand strategy, market research, product selection, listing optimization, advertising, DTC site operations, social media, influencer marketing, **overseas-buyer outbound prospecting**, and **earned-media press discovery**.

Two formats:
- **Single-file skills** (37) — one `.md` file each, drop into your AI IDE's skill directory.
- **Multi-file skill packages** (3, all under `outbound-prospecting/`) — `SKILL.md` + `references/` + `templates/` (incl. Python scripts and CSV trackers). Point your AI IDE at the package directory.

Plus **4 standalone tools** under `tools/` (Python utilities used by skills, also runnable independently): `backlink-kol-extractor`, `trustpilot`, `linktree-expander`, `contact-extractor`.

### Skill Map (40 skills across 10 chains)

```
                        ┌─────────────────────────────────────┐
                        │     Brand Strategy Chain (10)        │
                        │                                     │
  Market Scan ──► Track Hypothesis ──► Deep Validation ──► Strategy Plan
       │                                                       │
       │         Annual Plan ◄── Budget Ops                    │
       │                                                       ▼
       │                                    IMC Framework ──► Knowledge Base
       │                                         │
       │              A/B Compare    Chart Visualize   GTM Launch
       │                                         │
       ▼                                         ▼
  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │ Amazon Chain (14) │   │ DTC Site (4)     │   │ Social & KOL (5) │
  │                  │   │                  │   │                  │
  │ Selection        │   │ SEO Diagnostic   │   │ TikTok Growth    │
  │ Shortlist        │   │ SEO Playbook     │   │ YouTube Ops      │
  │ Market Research  │   │ SEM Ads          │   │ Content Calendar │
  │ IP Risk          │   │ Conversion UX    │   │ Influencer Mktg  │
  │ Supplier         │   └──────────────────┘   │ User Lifecycle   │
  │ Keywords         │                          └──────────────────┘
  │ Listing Copy     │   ┌──────────────────┐   ┌──────────────────┐
  │ Main Image       │   │ Offline (1)      │   │ VOC Tools (2)    │
  │ A+ Content       │   │                  │   │                  │
  │ Compliance       │   │ US Retail        │   │ Trustpilot Quick │
  │ Pre-Launch       │   └──────────────────┘   │ Trustpilot Deep  │
  │ Ad Architecture  │                          └──────────────────┘
  │ Weekly Ad Review │
  │ Ad Diagnosis     │
  └──────────────────┘
```

---

### Brand Strategy Chain (10 skills)

**4-Round Analysis Pipeline + Planning + Execution + Tools**

| Skill | What it does |
|-------|-------------|
| [brand-market-scan](brand-strategy/brand-market-scan.md) | Round 1: Market panoramic scan — 4-layer user insight, VOC matrix, competitive landscape, Semrush auto-scan |
| [brand-track-hypothesis](brand-strategy/brand-track-hypothesis.md) | Round 2: Track hypothesis generation — 3-5 market tracks, DTNICE classification, GTM flywheel |
| [brand-deep-validation](brand-strategy/brand-deep-validation.md) | Round 3: Deep hypothesis validation — 5D framework, SEO traffic model, benchmark cases, Zone 4 |
| [brand-strategy-plan](brand-strategy/brand-strategy-plan.md) | Round 4: Brand strategy & execution — 7-element positioning, 4 pillars, pricing, narrative, roadmap |
| [brand-imc-framework](brand-strategy/brand-imc-framework.md) | IMC integrated marketing — Audience/User dual-path, 6-stage funnel, channel mix, execution calendar |
| [brand-annual-plan](brand-strategy/brand-annual-plan.md) | Annual planning — BSC scorecard, 52-week calendar, quarterly OKRs, resource allocation |
| [brand-budget-ops](brand-strategy/brand-budget-ops.md) | Budget planning & control — 10-category budget model, monthly tracking, ROI by channel |
| [brand-knowledge-base](brand-strategy/brand-knowledge-base.md) | Obsidian knowledge base — batch-creates 30-50 interlinked .md files from all rounds |
| [brand-ab-compare](brand-strategy/brand-ab-compare.md) | 8-dimension A/B quality comparison between two brand strategy report sets |
| [brand-chart-visualize](brand-strategy/brand-chart-visualize.md) | Auto-generate charts (radar, bar, waterfall, scatter, etc.) via AntV API for all reports |

### Amazon Operations Chain (14 skills)

| Phase | Skill | What it does |
|-------|-------|-------------|
| Selection | [amazon-product-selection](amazon/amazon-product-selection.md) | Score and rank Top 30 potential products |
| Selection | [amazon-product-shortlist](amazon/amazon-product-shortlist.md) | Feasibility screening, GTM flywheel check, Go-List |
| Research | [amazon-market-research](amazon/amazon-market-research.md) | Full market research: VOC matrix, competitor teardown, SWOT |
| Research | [amazon-ip-risk-assessment](amazon/amazon-ip-risk-assessment.md) | Patent + trademark risk, design comparison, risk rating |
| Research | [amazon-supplier-decision](amazon/amazon-supplier-decision.md) | Supplier evaluation, cost breakdown, red flag detection |
| Listing | [amazon-keyword-research](amazon/amazon-keyword-research.md) | Keyword library: 3-tier CPC, COSMO/Rufus/A10 SEO |
| Listing | [amazon-listing-copywriter](amazon/amazon-listing-copywriter.md) | Title, bullet points, A+ description, Search Terms |
| Listing | [amazon-main-image-prompt](amazon/amazon-main-image-prompt.md) | Main + secondary image design briefs and AI prompts |
| Listing | [amazon-aplus-image-prompt](amazon/amazon-aplus-image-prompt.md) | A+ Content module layout, Brand Story, image prompts |
| Launch | [amazon-compliance-review](amazon/amazon-compliance-review.md) | 3-dimension audit: platform rules, legal/IP, AI search |
| Launch | [amazon-pre-launch-review](amazon/amazon-pre-launch-review.md) | Final pre-launch checklist across all SKILL outputs |
| Ads | [amazon-ad-architecture](amazon/amazon-ad-architecture.md) | PPC campaign structure: SP/SB/SD/SBV, budget, bid strategy |
| Ads | [amazon-weekly-ad-review](amazon/amazon-weekly-ad-review.md) | Weekly ad review: ACoS/TACoS, Search Terms, action list |
| Ads | [amazon-ad-diagnosis](amazon/amazon-ad-diagnosis.md) | Existing product diagnosis: 4-stage optimization pipeline |

### DTC Site & Traffic (4 skills)

| Skill | What it does |
|-------|-------------|
| [dsite-seo-diagnostic](brand-strategy/dsite-seo-diagnostic.md) | **NEW** — Entry-orchestrator skill for live-site SEO traffic-drop diagnostics. 7-dimension diagnosis (traffic curve / keyword loss / single-point risk / i18n pollution / backlink quality / content ROI / KPI audit) → algorithm-event alignment → restart roadmap. Chains `xlsx` / `dsite-seo-playbook` / `trustpilot-voc-deep` / `competitors-analysis` / `backlink-kol-extractor` / `report-pdf-export`. Output: deliverable PDF (A4 landscape, hides internal SKILL refs). |
| [dsite-seo-playbook](brand-strategy/dsite-seo-playbook.md) | Full SEO playbook: technical audit, keyword strategy, content plan, Core Web Vitals |
| [dsite-sem-ads](brand-strategy/dsite-sem-ads.md) | SEM & paid ads: 10-platform comparison, AIPL funnel, budget allocation |
| [dsite-conversion-ux](brand-strategy/dsite-conversion-ux.md) | Conversion rate optimization: 6-module CRO audit, UX best practices |

### Social Media & Content (3 skills)

| Skill | What it does |
|-------|-------------|
| [tiktok-growth](brand-strategy/tiktok-growth.md) | TikTok full-funnel growth: content strategy, TikTok Shop, livestream, paid ads |
| [youtube-channel-ops](brand-strategy/youtube-channel-ops.md) | YouTube channel operations: content strategy, SEO, monetization |
| [social-content-calendar](brand-strategy/social-content-calendar.md) | Social media content calendar: multi-platform scheduling, content pillars |

### VOC & Review Analysis (2 skills) — NEW in v3.1

| Skill | What it does |
|-------|-------------|
| [trustpilot-voc-quick](brand-strategy/trustpilot-voc-quick.md) | 5-min WebFetch scan: overall rating, star distribution, recent review summaries. Ideal for brand scanning Step 0 or competitor comparison |
| [trustpilot-voc-deep](brand-strategy/trustpilot-voc-deep.md) | Full pipeline (15-40 min): Selenium scraper with proxy rotation + sentiment analysis + LDA topic modeling + AI-powered deep insights. Uses `tools/trustpilot/` Python toolkit with **AntV visualization** for report-style consistency |

### KOL & User Operations (2 skills)

| Skill | What it does |
|-------|-------------|
| [influencer-marketing](brand-strategy/influencer-marketing.md) | KOL/influencer marketing: 5-tier pyramid, ROI tracking, contract templates |
| [user-lifecycle-ops](brand-strategy/user-lifecycle-ops.md) | User lifecycle management: 5-stage funnel, retention curves, churn analysis |

### GTM & Offline (2 skills)

| Skill | What it does |
|-------|-------------|
| [brand-gtm-launch](brand-strategy/brand-gtm-launch.md) | New product GTM launch: 7-step framework, timeline, channel coordination |
| [offline-retail-us](brand-strategy/offline-retail-us.md) | US offline retail: 8-tier channel analysis, readiness assessment, cost model |

### Outbound Prospecting (3 skills) — v3.4 adds press discovery

End-to-end pipelines for finding overseas B2B decision-makers, KOLs, and journalists, then converting them into ready-to-message lead sheets. Each skill is a multi-file package with `SKILL.md` + scripts + references + templates.

| Skill | What it does |
|-------|-------------|
| [google-whatsapp-prospecting](outbound-prospecting/google-whatsapp-prospecting/SKILL.md) | Google-dork → WhatsApp lead pipeline. 15+ search formulas (mobile-prefix narrowed), 30+ countries with B2B-platform / time-zone / compliance flags, full GDPR-CASL-CCPA-UWG compliance reference, multi-language outreach playbook (EN/ES/PT/FR/AR), SerpAPI batch script + `wa.me` validator. |
| [linkedin-prospecting](outbound-prospecting/linkedin-prospecting/SKILL.md) | Google/Bing/Yandex/Wayback reverse-search of LinkedIn → enrichment via Apollo/Snov/Hunter/Lusha/Wiza → 4-touch outreach (CR → DM → follow-up → channel-switch). 50+ localized role keywords across 8 languages, LinkedIn ToS + quota reference, 12 DM templates across 5 archetypes (incl. voice-note opener), reply-handling matrix. |
| [media-press-discovery](outbound-prospecting/media-press-discovery/SKILL.md) — **NEW v3.4** | Muckrack-anchored journalist DB pipeline. 5 scripts (`discover_journalists` / `find_articles` / `guess_emails` / `score_and_export` / `merge_partitions`) + shared `_fetcher.py` with 4 backends (requests / remote-chrome / apify / html-dir for Cloudflare-protected pages). Multi-machine partition-merge workflow. Outputs ranked `pitch_db.csv` with journalist contacts + last topical coverage. |

Sister skills — same 4-stage shape (Search → Enrich → Outreach → Compliance), different channels. Designed to run in parallel for the same lead set.

### Tools (standalone utilities)

Standalone Python utilities under `tools/`. Each is a multi-file package with own `SKILL.md` + `scripts/` + `references/` + `templates/`. Used by skills above conditionally; also runnable independently.

| Tool | What it does | Used by |
|------|-------------|---------|
| [backlink-kol-extractor](tools/backlink-kol-extractor/SKILL.md) | Extract KOL / media / affiliate prospects from Semrush competitor backlink xlsx data — 3-step methodology (domain pattern → cross-competitor validation → social handle extraction) | `influencer-marketing` (Step 2.5), `dsite-seo-playbook` (Step 4.6) — both conditionally activated when Semrush data is provided |
| [trustpilot](tools/trustpilot/) — **rebuilt v3.4** | Selenium-based Trustpilot review scraper with chained-proxy rotation, AI sentiment + topic analysis, multi-language. v3.4 rebuild: modern data-* attribute selectors (replaces 110-line sibling-XPath fallback chain), desktop-UA pin (Trustpilot serves snippet-only DOM to mobile UA), `--cutoff_date` arg, `--skip_ai` mode, redacted hardcoded proxy creds (env-var loading) | `trustpilot-voc-quick`, `trustpilot-voc-deep` |
| [linktree-expander](tools/linktree-expander/SKILL.md) — **NEW v3.4** | Batch-enrich Linktree handles into per-creator profiles via `__NEXT_DATA__` JSON parsing. Extracts IG / TikTok / YouTube / Substack / Twitter / podcast handles + bio + outbound link categorization + handle-match-scored personal_site (with `NON_PERSONAL_HOSTS` blocklist for shorteners / aggregators / docs / scheduling) | KOL discovery pipelines downstream of `backlink-kol-extractor` |
| [contact-extractor](tools/contact-extractor/SKILL.md) — **NEW v3.4** | Multi-source contact email extraction with confidence tiering. Sources: personal_site `/about` `/contact` `/press` paths (mailto/text) + YouTube Data API v3 description + Apple Podcasts RSS owner + email pattern guess (with `--verify` SMTP MX probe / Hunter.io). Outputs ranked `contact_email_1..3` + `confidence` (high / medium / low / none) | KOL outreach prep, post `linktree-expander` or `media-press-discovery` |

See [tools/README.md](tools/README.md) for standalone usage.

---

### Key Features

- **39 Skills, 10 Chains** — Complete coverage from brand strategy to daily operations to overseas-buyer outbound
- **Data Verification Layer** — Every skill includes mandatory verification; estimates are explicitly flagged with ⚠️
- **Chart Visualization** — 21 skills auto-generate charts (radar, bar, waterfall, scatter, funnel, etc.) via AntV API
- **Semrush Integration** — Brand strategy skills auto-scan local Semrush xlsx/PDF data as high-confidence source
- **VOC Matrix** — Mention frequency × satisfaction matrix to identify unmet needs
- **GTM Flywheel** — Market → Product → Marketing → Operations four-wheel evaluation
- **AI Search Ready** — Optimized for Amazon Rufus, COSMO knowledge graph, and GEO
- **Multi-Platform** — Works on Claude Code, Google Antigravity, OpenClaw, and any AI IDE

### Installation

**Claude Code (recommended):**
```bash
git clone https://github.com/noique/cross-border-ecommerce-skills.git

# Single-file skills → ~/.claude/commands/
cp cross-border-ecommerce-skills/brand-strategy/*.md ~/.claude/commands/
cp cross-border-ecommerce-skills/amazon/*.md ~/.claude/commands/

# Multi-file skill packages → ~/.claude/skills/ (one directory per skill)
cp -r cross-border-ecommerce-skills/outbound-prospecting/google-whatsapp-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/outbound-prospecting/linkedin-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/tools/backlink-kol-extractor ~/.claude/skills/
```

**Google Antigravity / OpenClaw / Any AI IDE:**
Copy `.md` files (single-file skills) or whole directories (multi-file packages) into your skill directory.

### Model Requirements

| Tier | Quality | Models (as of April 2026) |
|------|---------|--------------------------|
| Recommended | Full execution, verification works | Claude Opus 4.6 / Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro |
| Usable | Structure OK, may skip verification | DeepSeek V4 / V3.2, Llama 4, Qwen 3.5 (72B+), GLM-5.1 |
| Not recommended | Sections missing, checks fail | Models under 30B parameters |

Key requirements: long context (8K+ input), strong instruction following, Chinese-English bilingual, tool use / web browsing.

---

## 中文说明

### 这是什么？

一套 **39 个跨境电商 AI 技能模板**，覆盖品牌战略→选品→调研→文案→广告→独立站→社媒→红人→线下渠道→海外开发的全流程自动化。

两种格式：
- **单文件技能（37 个）** — 一个 `.md` 文件，放入 AI IDE 技能目录即可使用
- **多文件技能包（2 个，全部在 `outbound-prospecting/`）** — `SKILL.md` + `references/` + `templates/`（含 Python 脚本和 CSV 跟踪表），将整个目录指向 AI IDE

### 技能矩阵（39 个技能，10 条链路）

| 链路 | 数量 | 技能 |
|------|------|------|
| **品牌战略链** | 10 | 市场扫描 → 赛道假设 → 深度验证 → 品牌战略 → IMC框架 → 年度规划 → 预算管控 → 知识库 → A/B对比 → 图表可视化 |
| **Amazon 运营链** | 14 | 选品 → 筛选 → 调研 → IP排查 → 供应商 → 关键词 → 文案 → 主图 → A+ → 合规 → 复查 → 广告架构 → 周报 → 诊断 |
| **独立站流量** | 4 | **SEO 全链路诊断（NEW v3.3）** → SEO全链路规划 → SEM广告 → 转化率优化 |
| **社媒与内容** | 3 | TikTok增长 → YouTube运营 → 内容日历 |
| **VOC 评论分析** | 2 | Trustpilot 快速扫描 → Trustpilot 深度分析（爬虫+情感+LDA+AI 归纳） |
| **红人与用户** | 2 | 红人营销 → 用户生命周期 |
| **GTM 执行** | 1 | 新品上市规划 |
| **线下渠道** | 1 | 美国线下零售 |
| **海外开发（NEW v3.2）** | 2 | Google→WhatsApp 反查开发（15+ 公式 + 30+ 国家 + 多语言话术 + 合规手册）→ Google→LinkedIn 反查开发（CR + 12 DM 模板 + 5 种 archetype + 8 语言职位词 + LinkedIn ToS 限额表） |

### 核心特色

- **39 技能 × 10 链路** — 从战略到执行到海外开发全覆盖
- **数据验证层** — 每个技能内置强制验证，推测数据标 ⚠️
- **图表可视化** — 21 个技能自动生成图表（雷达/柱状/瀑布/散点/漏斗等），调用 AntV API
- **Semrush 集成** — 品牌战略技能自动扫描本地 Semrush 数据
- **VOC 用户洞察** — 提及量×满意度二维分析
- **GTM 飞轮** — 市场→产品→营销→运营四维评估
- **AI 搜索适配** — Amazon Rufus / COSMO / GEO 优化
- **多平台兼容** — Claude Code / Antigravity / OpenClaw / 任何 AI IDE

### 安装方式

```bash
# Claude Code 一键安装
git clone https://github.com/noique/cross-border-ecommerce-skills.git

# 单文件技能 → ~/.claude/commands/
cp cross-border-ecommerce-skills/brand-strategy/*.md ~/.claude/commands/
cp cross-border-ecommerce-skills/amazon/*.md ~/.claude/commands/

# 多文件技能包 → ~/.claude/skills/（每个技能一个目录）
cp -r cross-border-ecommerce-skills/outbound-prospecting/google-whatsapp-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/outbound-prospecting/linkedin-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/tools/backlink-kol-extractor ~/.claude/skills/
```

### 模型要求

| 层级 | 效果 | 代表模型（2026 年 4 月） |
|------|------|------------------------|
| 推荐 | 完整执行，验证步骤生效 | Claude Opus 4.6 / Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro |
| 可用 | 结构完整，可能跳过验证 | DeepSeek V4 / V3.2、Llama 4、Qwen 3.5 (72B+)、GLM-5.1 |
| 不建议 | 章节缺失，检查失效 | 30B 以下参数模型 |

---

## Changelog

### v3.4 (2026-05-06)
- **New `outbound-prospecting/media-press-discovery/`** multi-file skill — Muckrack-anchored journalist DB pipeline. 5 scripts (`discover_journalists` / `find_articles` / `guess_emails` / `score_and_export` / `merge_partitions`) + shared `_fetcher.py` with 4 backends (`requests` / `remote-chrome` / `apify` / `html-dir`) for Cloudflare-protected pages. Multi-machine partition-merge workflow.
- **New `tools/linktree-expander/`** — batch-enrich Linktree handles via `__NEXT_DATA__` JSON parsing. Handle-match scoring for `personal_site` + `NON_PERSONAL_HOSTS` blocklist (30+ shorteners / aggregators / docs / scheduling tools). Verified 44/45 ok on a 45-handle pilot.
- **New `tools/contact-extractor/`** — multi-source email extraction with confidence tiering. Sources: `personal_site` `/about` `/contact` `/press` (mailto / text) + YouTube Data API v3 description + Apple Podcasts RSS owner + email pattern guess. Optional `--verify` SMTP MX probe / Hunter.io. Outputs ranked `contact_email_1..3` + `confidence` (high / medium / low / none).
- **`tools/trustpilot/` rebuilt**: modern data-* attribute selectors (replaces 110-line sibling-XPath fallback chain that broke on Trustpilot's 2026 DOM update), desktop-UA pin (Trustpilot serves snippet-only DOM to mobile UAs — major silent failure mode), `?sort=recency` URL flag (relevance widget served snippet-only DOM for some brands), `--cutoff_date YYYY-MM-DD` arg (efficient time-bounded scrapes), `--skip_ai` mode bypasses broken `generate_report()` signature, redacted hardcoded SOCKS5 proxy creds in `config.py` (now env-var loaded).
- Total: **40 skills** across 10 chains. Tools count: 4 (was 1).

### v3.3 (2026-04-27)
- **New entry-orchestrator skill** `dsite-seo-diagnostic` (single-file, under `brand-strategy/`) — for live-site SEO traffic-drop diagnostics + restart roadmap.
  - **7-dimension diagnostic framework**: traffic curve (algorithm-downgrade signature) / keyword loss structure / single-point-failure risk / multilingual-Markets URL pollution / backlink quality (DS distribution + anchor text pathology) / content ROI (HCU-hit detection) / KPI body audit (process-volume vs outcome).
  - **Algorithm-event alignment**: traffic curve auto-aligned with public Google Core / HCU / Spam Update timeline (rolling 24-month window).
  - **Restart roadmap**: 4-phase plan (stop-the-bleeding → cleanse → content rebuild → off-site signals) anchored on the `dsite-seo-playbook` 6-step framework.
  - **Multi-skill orchestration**: chains `xlsx` → `dsite-seo-playbook` → `trustpilot-voc-deep` / `competitors-analysis` / `backlink-kol-extractor` → `report-pdf-export`. Hides internal SKILL refs in deliverable.
  - **Standard PDF deliverable** (A4 landscape, deep-blue header, zebra rows, page-numbered) via `report-pdf-export`.
  - **Use cases**: traffic anomaly investigation, pre-vendor-replacement independent diagnostics, annual SEO health check, post-Core-Update impact assessment, post-migration audit, multilingual / Shopify Markets pollution audit.
- Total: **39 skills** across 10 chains.

### v3.2 (2026-04-26)
- **New Outbound Prospecting chain (2 multi-file skill packages)** under `outbound-prospecting/`:
  - `google-whatsapp-prospecting` — Google-dork → WhatsApp lead pipeline. 4-stage workflow (Search → Validate → Enrich → Outreach). 15+ search formula variants, 30+ countries with mobile-prefix narrowing + B2B platforms + time-zone send windows + compliance flags. Full GDPR / CASL / CCPA / UWG §7 / WhatsApp ToS compliance reference. Multi-language outreach playbook (EN/ES/PT/FR/AR). SerpAPI batch script + `wa.me` validator + lead-tracker CSV.
  - `linkedin-prospecting` — Google + Bing + Yandex + Wayback reverse-search of LinkedIn. Post-2024 Auth Wall workarounds. 50+ decision-maker role keywords localized into 8 languages with company-size-band gating (CEO targeting only valid for ≤500 employees). Enrichment-tool comparison (Apollo / Snov / Hunter / Lusha / Wiza) with cost + accuracy + legal context. LinkedIn ToS § 8.2 + 2026 quota table + account warm-up protocol. 4-touch outreach (Connection Request → DM → Follow-up → Channel-switch) with 12 DM templates across 5 archetypes (incl. voice-note opener), reply-handling matrix, native templates in PT/ES/FR/DE/AR/JA.
- **New format**: multi-file skill packages (SKILL.md + references/ + templates/ with Python helpers + CSV trackers), in addition to existing single-file `.md` skills.
- Total: **38 skills** across 10 chains.

### v3.1 (2026-04-14)
- **New VOC chain (2 skills)**: `/trustpilot-voc-quick` (5-min surface scan) and `/trustpilot-voc-deep` (full pipeline with sentiment analysis, LDA topic modeling, and AI-powered insights)
- **New tools directory**: `tools/trustpilot/` with Python toolkit for deep review analysis
- Total: **36 skills** across 9 chains

### v3.0 (2026-04-13)
- **12 new skills**: annual-plan, budget-ops, gtm-launch, seo-playbook, sem-ads, conversion-ux, tiktok-growth, youtube-ops, influencer-marketing, user-lifecycle-ops, social-content-calendar, offline-retail-us
- **Chart visualization**: 21 skills now auto-generate charts via AntV API (radar, bar, column, pie, waterfall, scatter, line, funnel, sankey)
- **Unified footers**: All 36 skills now include GitHub open source link
- Total: **34 skills** across 8 chains

### v2.1 (2026-04-12)
- Added `/brand-ab-compare` SKILL
- Semrush local data auto-scan in Step 0
- Data gap reporting, minimum depth constraints
- SEO traffic model validation in Round 3
- Auto knowledge base trigger in IMC

### v2.0 (2026-04-11)
- Real-time data collection layer added to 3 brand strategy SKILLs

### v1.0 (2026-04-07)
- Initial release: 6 brand strategy + 14 Amazon skills (20 total)

---

## License

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

Free to use, share, and adapt with credit.

## Author

Created by **Alex / 黄子阳** — [ckcm.us](https://ckcm.us)

### Contact / 联系方式

有定制化调研需求、品牌咨询、或技能使用问题，扫码加微信：

<img src="wechat-qr.png" alt="WeChat QR Code" width="200">
