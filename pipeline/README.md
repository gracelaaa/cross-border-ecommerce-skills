# 需求信号采集 Pipeline

从 10 个公开数据源采集出海选品需求信号，统一存储到 SQLite 数据库。

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 目录结构要求

Pipeline 依赖 `tools/fetchlib` 模块，确保目录结构如下：

```
cross-border-ecommerce-skills/
├── tools/
│   └── fetchlib/
│       └── fetchlib.py          # 网页抓取工具库
└── pipeline/
    ├── run.py                   # ← 入口
    ├── config.py
    ├── db.py
    ├── base.py
    ├── schema.sql
    ├── requirements.txt
    ├── demand_signals.db        # 运行后生成
    └── collectors/
        ├── amazon.py
        ├── trustpilot.py
        ├── producthunt.py
        ├── hackernews.py
        ├── github_issues.py
        ├── google_trends.py
        ├── youtube.py
        ├── tiktok.py
        ├── reddit.py
        └── amz_dataset.py
```

### 3. 运行

```bash
# 查看数据库统计（不采集）
python3 run.py --stats

# 运行全部 10 个采集器
python3 run.py

# 只运行指定采集器
python3 run.py --only amazon reddit hackernews

# 跳过指定采集器
python3 run.py --skip tiktok amz_dataset
```

### 4. 采集器名称对照

| CLI 名称 | 文件 | 数据源 |
|----------|------|--------|
| `amazon` | amazon.py | Amazon 搜索页 |
| `trustpilot` | trustpilot.py | Trustpilot 评论 |
| `producthunt` | producthunt.py | Product Hunt |
| `hackernews` | hackernews.py | Hacker News |
| `github` | github_issues.py | GitHub Issues |
| `google_trends` | google_trends.py | Google Trends |
| `youtube` | youtube.py | YouTube 搜索 |
| `tiktok` | tiktok.py | TikTok（反爬限制，可能 0 条） |
| `reddit` | reddit.py | Reddit（需 BrowserAct） |
| `amz_dataset` | amz_dataset.py | Amazon Reviews 2023 数据集 |

## Reddit 采集器额外要求

Reddit 采集器使用 BrowserAct CLI 通过 Google `site:reddit.com` 搜索间接获取数据，需要：

1. 安装 BrowserAct CLI 工具
2. 在 `config.py` 中配置：
   - `BROWSERACT_BIN`：BrowserAct 可执行文件路径
   - `BROWSERACT_DATA_DIR`：BrowserAct 数据目录
   - `BROWSERACT_BROWSER_ID`：已创建的浏览器实例 ID

如果不需要 Reddit 数据，可以用 `--skip reddit` 跳过。

## 数据库结构

### demand_signals 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| source | TEXT | 数据源名称 |
| signal_type | TEXT | 信号类型（见下表） |
| title | TEXT | 标题 |
| content | TEXT | 正文内容 |
| url | TEXT | 原始链接（UNIQUE） |
| score | REAL | 评分/热度 |
| posted_at | TEXT | 发布时间 |
| keywords | TEXT | 关键词（JSON 数组） |
| metadata | TEXT | 元数据（JSON） |
| collected_at | TEXT | 采集时间 |

### 信号类型

| 类型 | 说明 |
|------|------|
| pain_point | 用户痛点/抱怨 |
| purchase_intent | 购买意向 |
| trend | 趋势信号 |
| feature_request | 功能需求 |
| review | 产品评论 |
| discussion | 社区讨论 |
| product_listing | 产品列表 |
| video_content | 视频内容 |

### collection_runs 表

记录每次采集运行的日志（采集器名称、状态、信号数、耗时、错误信息）。

## 增量更新

数据库使用 `UNIQUE(source, url)` 约束 + `INSERT OR IGNORE` 策略：
- 重复运行不会产生重复数据
- 同一 URL 只保留第一次采集的记录
- 如需刷新某条数据，需先删除再重新采集

## 查询数据

```bash
# 用 sqlite3 命令行查询
sqlite3 demand_signals.db "SELECT source, COUNT(*) FROM demand_signals GROUP BY source;"

# 或用 Python
python3 -c "
import sqlite3
conn = sqlite3.connect('demand_signals.db')
for row in conn.execute('SELECT source, signal_type, title FROM demand_signals LIMIT 10'):
    print(row)
"
```
