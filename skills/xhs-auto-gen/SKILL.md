# XHS Auto Gen Skill

自动化小红书笔记生成 Skill。每天从 GitHub data 分支抓取跨境电商需求数据，筛选 Reddit 卖家痛点，生成小红书风格笔记。

## 链路流程

```
GitHub data 分支 (demand_signals.json)
    ↓ curl 下载
筛选 Reddit + 跨境电商关键词
    ↓
按内容质量排序，选出最佳候选
    ↓
Humanizer 去 AI 味处理
    ↓
输出小红书笔记 .md 文件
    ↓
GitHub Actions 每天 09:00 自动运行
```

## 文件结构

```
skills/xhs-auto-gen/
├── SKILL.md                    # 本文件
├── pipeline.py                 # 核心 pipeline 脚本
├── requirements.txt            # Python 关键词
└── .github/
    └── workflows/
        └── xhs-auto-gen.yml    # GitHub Actions 定时任务配置
```

## 使用方式

### 本地运行

```bash
cd skills/xhs-auto-gen
pip install -r requirements.txt
python pipeline.py
```

### GitHub Actions 自动运行

每天 09:00 UTC（北京时间 17:00）自动运行，生成笔记后 commit 到仓库。

## 配置项

在 `pipeline.py` 顶部修改：

| 配置 | 默认值 | 说明 |
|------|--------|------|
| `DATA_URL` | GitHub raw URL | 需求数据源 |
| `OUTPUT_DIR` | `./output` | 笔记输出目录 |
| `MAX_NOTES_PER_RUN` | 3 | 每次运行最多生成几篇笔记 |
| `MIN_CONTENT_LENGTH` | 300 | 帖子最少字符数 |
| `KEYWORDS` | 见脚本 | 跨境电商关键词列表 |

## 输出格式

每次运行在 `output/` 目录下生成：

```
output/
├── 2026-07-12_amazon-loses-sales-3-seconds.md
├── 2026-07-12_dropshipping-supplier-issues.md
└── ...
```

文件名格式：`{date}_{slug}.md`

## 注意事项

1. **AI 生成部分**：当前版本使用模板 + 规则生成，不依赖外部 LLM API
2. **如需接入 LLM**：在 `generate_note()` 函数中替换为 API 调用
3. **发布到小红书**：生成后需人工审核，然后通过 xiaohongshu-mcp 发布
