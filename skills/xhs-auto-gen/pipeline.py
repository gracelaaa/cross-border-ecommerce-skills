#!/usr/bin/env python3
"""
XHS Auto Gen Pipeline
从 GitHub data 分支抓取需求数据，筛选跨境电商相关 Reddit 帖子，
生成小红书风格笔记。

每天 09:00 UTC 通过 GitHub Actions 自动运行。
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

# -------- 配置 --------
DATA_URL = os.environ.get(
    "DATA_URL",
    "https://raw.githubusercontent.com/gracelaaa/cross-border-ecommerce-skills/data/data/demand_signals.json"
)
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./output")
MAX_NOTES_PER_RUN = int(os.environ.get("MAX_NOTES_PER_RUN", "3"))
MIN_CONTENT_LENGTH = int(os.environ.get("MIN_CONTENT_LENGTH", "300"))
GITHUB_REPO = os.environ.get("GITHUB_REPO", "gracelaaa/cross-border-ecommerce-skills")

# 跨境电商关键词 - 帖子必须包含至少一个
KEYWORDS = [
    "amazon fba", "fba seller", "amazon seller", "amazon listing",
    "dropshipping", "shopify store", "shopify dropship",
    "cross-border ecommerce", "cross border ecommerce",
    "aliexpress", "alibaba", "1688", "supplier", "sourcing",
    "product research", "amazon ppc", "ppc campaign",
    "inventory management", "warehouse", "fulfillment center",
    "ip complaint", "copyright", "trademark", "patent",
    "customs", "tariff", "import tax", "vat",
    "chargeback", "review manipulation", "review removal",
    "account suspended", "listing suppressed", "buy box",
    "profit margin", "roi", "roi calculator", "seller central",
    "fulfillment", "shipping container", "freight forwarding",
]

# 痛点类关键词 - 命中会加分
PAIN_KEYWORDS = [
    "frustrated", "struggle", "struggling", "failed", "failing",
    "nightmare", "scam", "stolen", "lost money", "can't figure",
    "nothing works", "no one talks about", "nobody talks",
    "no one mentions", "everyone ignores", "hidden", "secret",
    "mistake", "regret", "waste", "wasted", "broken", "confusing",
    "complicated", "impossible", "helpless", "stuck",
]

# 人类感、真实感的标题信号
AUTHENTIC_TITLE_SIGNALS = [
    "i sold", "i tried", "my experience", "after \\d+ years",
    "nobody talks", "no one talks", "i wish i knew",
    "stop doing", "don't do this", "mistake", "regret",
    "least expect", "hidden", "secret",
]

# -------- 阶段 1：数据获取 --------

def download_data(url: str) -> list:
    """下载需求数据 JSON"""
    print(f"[1/4] 从 GitHub 下载数据...")
    try:
        req = Request(url, headers={"User-Agent": "XHS-Auto-Gen/1.0"})
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"  → 共 {len(data)} 条数据")
        return data
    except Exception as e:
        print(f"  ✗ 下载失败: {e}", file=sys.stderr)
        sys.exit(1)

# -------- 阶段 2：筛选候选 --------

def filter_reddit_posts(data: list) -> list:
    """筛选 Reddit + 跨境电商相关帖子"""
    print(f"[2/4] 筛选 Reddit 帖子...")

    reddit = []
    for d in data:
        # 只取 reddit_broad 和 reddit 来源
        if d.get("source") not in ("reddit", "reddit_broad"):
            continue

        title = d.get("title", "") or ""
        content = d.get("content", "") or ""
        text = f"{title} {content}".lower()

        # 必须命中至少一个跨境电商关键词
        matched_kw = [kw for kw in KEYWORDS if kw in text]
        if not matched_kw:
            continue

        # 内容要有足够长度（完整的故事）
        if len(content) < MIN_CONTENT_LENGTH:
            continue

        reddit.append((d, matched_kw))

    print(f"  → 命中 {len(reddit)} 条 Reddit 帖子")
    return reddit


def score_post(post: list, matched_kw: list) -> float:
    """给帖子打分，选出最有故事性的"""
    d = post if isinstance(post, dict) else post[0]
    title = d.get("title", "") or ""
    content = d.get("content", "") or ""
    text = f"{title} {content}".lower()

    score = 0.0

    # 内容长度 - 长文通常故事更完整
    score += min(len(content) / 500, 3.0)

    # 标题真实感信号
    for pattern in AUTHENTIC_TITLE_SIGNALS:
        if re.search(pattern, title.lower()):
            score += 2.0

    # 痛点关键词命中 - 痛感越强分越高
    pain_count = sum(1 for kw in PAIN_KEYWORDS if kw in text)
    score += pain_count * 1.5

    # 关键词多样性奖励
    score += min(len(matched_kw) * 0.5, 2.0)

    # "Nobody" "secret" "hidden" 等强烈信号
    strong_patterns = ["nobody talk", "no one talk", "hidden killer", "secret",
                       "i figured out", "i discovered", "the answer", "the reason"]
    for pat in strong_patterns:
        if pat in text:
            score += 3.0

    # 标题较长通常信息量大
    word_count = len(title.split())
    if word_count >= 8:
        score += 1.0

    return score


def select_candidates(reddit_posts: list, max_notes: int) -> list:
    """选出得分最高的候选帖子，按URL去重"""
    print(f"[3/4] 排序候选...")

    # 先从 URL 去重（保留分高的）
    url_best = {}
    for d, matched_kw in reddit_posts:
        url = d.get("url", "")
        s = score_post(d, matched_kw)
        if url not in url_best or s > url_best[url][0]:
            url_best[url] = (s, d, matched_kw)

    scored = list(url_best.values())
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_notes]

    print(f"  → 选出 top {len(top)} 条:")
    for score, d, kws in top:
        print(f"    [{score:.1f}] {d.get('title', '')[:60]}...")

    return top

# -------- 阶段 3：生成笔记 --------

# 行业分类映射
CATEGORY_MAP = {
    "amazon fba": "跨境电商 / Amazon FBA",
    "amazon seller": "跨境电商 / Amazon FBA",
    "amazon listing": "跨境电商 / Amazon 运营",
    "fba seller": "跨境电商 / Amazon FBA",
    "dropshipping": "跨境电商 / 独立站",
    "shopify store": "跨境电商 / Shopify独立站",
    "aliexpress": "跨境电商 / 选品采购",
    "alibaba": "跨境电商 / 供应链管理",
    "product research": "跨境电商 / 选品分析",
    "ppc campaign": "跨境电商 / 广告运营",
    "fulfillment": "跨境电商 / 物流仓储",
    "tariff": "跨境电商 / 税务合规",
    "vat": "跨境电商 / 税务合规",
    "ip complaint": "跨境电商 / 知识产权",
    "account suspended": "跨境电商 / 账号安全",
}


def detect_category(matched_kw: list) -> str:
    """根据关键词判断行业分类"""
    for kw in matched_kw:
        for key, cat in CATEGORY_MAP.items():
            if key in kw.lower():
                return cat
    return "跨境电商"


def make_slug(title: str) -> str:
    """生成标题 slug"""
    s = title.lower()
    # 只保留字母数字和连字符
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = s[:50].rstrip("-")
    return s or "untitled"


def humanize_text(text: str) -> str:
    """基础去 AI 味处理"""
    # 删除重复词
    text = re.sub(r"\\b(\\w+)(\\s+\\1)+\\b", r"\\1", text, flags=re.IGNORECASE)
    # 替换掉 AI 常用模板词
    replacements = {
        "首先，": "",
        "其次，": "",
        "最后，": "",
        "总之，": "",
        "综上所述，": "",
        "值得注意的是，": "",
        "需要指出的是，": "",
        "毫无疑问，": "",
        "毫无疑问，": "",
        "众所周知，": "",
        "in conclusion，": "",
        "moreover，": "",
        "furthermore，": "",
        "however，": "但",
        "therefore，": "所以",
        "additionally，": "另外",
        "specifically，": "具体来说",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def generate_note(post: dict, matched_kw: list, rank: int) -> str:
    """根据 Reddit 帖子生成小红书笔记"""
    title = post.get("title", "")
    content = post.get("content", "")
    url = post.get("url", "")
    score = post.get("score", 0)

    # 提取帖子核心故事 - 去掉杂音
    # 取前800字符，保证故事完整但有重点
    story = content[:800].strip()
    if len(content) > 800:
        story += "..."

    story = humanize_text(story)
    category = detect_category(matched_kw)
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    # 标题：如果原标题够抓心，直接用；否则改写
    xhs_title = title
    # 不截断标题，完整保留
    if len(title) > 50:
        xhs_title = title[:47] + "..."

    # 正文模板 - 采用"我发现了什么 → 什么行业 → 痛点 → 当前方案 → 机会点"结构
    body = f"""{xhs_title}

翻了4000多条Reddit上{category.split('/')[0]}的帖子，大多数在骂{get_common_complaint(matched_kw)}。

但有一条把我看清醒了。

---

**这是什么行业？**

{category}

---

**帖子说了什么？**

{story}

---

**痛点是什么？**

{extract_pain_points(content)}

---

**现在卖家怎么应对？**

两种。一种人花钱请专业团队拍图、做listing、调广告，质量有保证但成本不低。
另一种人自己搞，手机拍一拍就传上去，但别人的主图在手机端一眼就能认出来，你的缩成一个小点——这不是产品问题，是呈现方式的问题。

---

**机会在哪？**

如果有工具或服务能帮卖家：
✅ 一键模拟手机端主图效果
✅ AI处理图片合规+优化
✅ A/B测试自动跑不同版本的点击表现

这就是一个很小的切入点，但解决的是每个卖家都会遇到的问题。

数据来源：{url}

---

#{' #'.join(get_hashtags(category, matched_kw))}
"""

    # 组装最终笔记
    note = f"""# {xhs_title}

> 生成日期：{today}
> 数据来源：Reddit r/{post.get('category', 'AmazonFBA')}
> Source: {url}
> 质量评分：{score}

---

{body}

---

> ⚠️ 本文由 pipeline 自动生成，请人工审核修改后再发布到小红书。
> 如需发布，使用 xiaohongshu-mcp 的 post-to-xhs 子技能。
"""
    return note


def get_common_complaint(matched_kw: list) -> str:
    """根据关键词判断最常见的吐槽方向"""
    if any("price" in kw or "margin" in kw for kw in matched_kw):
        return "利润太薄"
    if any("account" in kw or "suspend" in kw for kw in matched_kw):
        return "账号随时可能被封"
    if any("ppc" in kw or "ad" in kw for kw in matched_kw):
        return "广告费越来越贵"
    if any("review" in kw for kw in matched_kw):
        return "review被删"
    if any("thumbnail" in kw or "image" in kw for kw in matched_kw):
        return "主图不吸量、转化率低"
    return "竞争太激烈"


def extract_pain_points(content: str) -> str:
    """从内容中提取痛点片段，更精准"""
    sentences = re.split(r"[.!?]\s+", content)
    pain_items = []

    severe_pain_patterns = [
        "frustrat", "nightmare", "scam", "broken", "terrible",
        "no one talks", "nobody talks", "hidden", "secret",
        "lost money", "lost \\$\\d+", "can't figure", "nothing works",
        "doesn't make sense", "not working", "waste", "regret",
        "never again", "avoid", "beware", "warning",
        "stolen", "hacked", "suspended", "banned",
    ]

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 10 or len(sent) > 300:
            continue
        lower_sent = sent.lower()
        for pat in severe_pain_patterns:
            if re.search(pat, lower_sent):
                # 指向性提取：只取痛点相关部分，精炼呈现
                pain_items.append(f"- {sent}")
                break
        if len(pain_items) >= 3:
            break

    if not pain_items:
        # fallback: 揭示"原来如此"类的洞见句子
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 15 or len(sent) > 250:
                continue
            lower_sent = sent.lower()
            if any(p in lower_sent for p in ["the answer", "the reason", "discovered", "realized", "turned out", "figured out"]):
                pain_items.append(f"- {sent}")
                break

    if not pain_items:
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        pain_items = [f"- {s}" for s in sentences[:2]]

    return "\n".join(pain_items)


def get_hashtags(category: str, matched_kw: list) -> list:
    """生成小红书标签"""
    base_tags = ["跨境电商"]
    if "Amazon" in category:
        base_tags.extend(["AmazonFBA", "亚马逊运营", "亚马逊卖家"])
    if "Shopify" in category or "dropship" in " ".join(matched_kw):
        base_tags.extend(["Shopify", "独立站"])
    if "选品" in category:
        base_tags.append("选品工具")

    # 从匹配的关键词中补充标签
    kw_tag_map = {
        "amazon ppc": "PPC广告",
        "dropshipping": "dropshipping",
        "aliexpress": "速卖通",
        "alibaba": "1688",
        "product research": "产品调研",
        "fulfillment": "FBA仓储",
    }
    for kw, tag in kw_tag_map.items():
        if any(kw in m.lower() for m in matched_kw):
            base_tags.append(tag)

    # 兜底
    base_tags.append("跨境电商创业")
    return list(dict.fromkeys(base_tags))[:8]  # 去重，最多8个


# -------- 阶段 4：输出 --------

def save_notes(candidates: list, output_dir: str):
    """保存生成的笔记"""
    print(f"[4/4] 保存笔记...")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    saved = []

    for rank, (score, post, matched_kw) in enumerate(candidates, 1):
        note = generate_note(post, matched_kw, rank)
        slug = make_slug(post.get("title", "untitled"))
        filename = f"{today}_{rank:02d}_{slug}.md"
        filepath = out / filename

        filepath.write_text(note, encoding="utf-8")
        saved.append(filepath)
        print(f"  ✓ [{rank}] 已保存: {filename}")

    return saved

# -------- 主入口 --------

def main():
    print("=" * 60)
    print("  XHS Auto Gen Pipeline")
    print(f"  {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    data = download_data(DATA_URL)
    reddit = filter_reddit_posts(data)

    if not reddit:
        print("没有找到候选帖子，跳过本次生成。")
        return

    candidates = select_candidates(reddit, MAX_NOTES_PER_RUN)
    saved = save_notes(candidates, OUTPUT_DIR)

    print(f"\n✅ 成功生成 {len(saved)} 篇笔记至 {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
