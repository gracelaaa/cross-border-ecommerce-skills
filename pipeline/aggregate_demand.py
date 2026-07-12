#!/usr/bin/env python3
"""
aggregate_demand.py — 需求信号聚合分析器

核心方法论（2026-07-09 用户洞察）：
  "1000 条稀疏信号没关系，只要 50 条在说类似的事，那件事就是真需求"

算法：
  1. 从 demand_signals.db 读取所有信号
  2. 按 category + signal_type 初步分桶
  3. 在桶内按关键词重叠度做简单聚类
  4. 对每个聚类计算：信号量、跨平台多样性、总热度、平均评分
  5. 输出排序后的"机会聚类"报告

用法：
  python3 aggregate_demand.py              # 打印报告到 stdout
  python3 aggregate_demand.py --top 20     # 只看 TOP 20
  python3 aggregate_demand.py --min 5      # 最少5条信号才算聚类
  python3 aggregate_demand.py --json       # JSON 格式输出
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ── 路径 ──────────────────────────────────────────────────────────────
PIPELINE_DIR = Path(__file__).parent
DB_PATH = PIPELINE_DIR / "demand_signals.db"

# ── 停用词（中英文）────────────────────────────────────────────────────
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "this", "that", "are", "was",
    "be", "as", "has", "had", "do", "did", "will", "would", "could",
    "should", "may", "can", "i", "my", "me", "we", "our", "you", "your",
    "he", "she", "they", "them", "his", "her", "their", "what", "which",
    "who", "how", "when", "where", "why", "not", "no", "yes", "so",
    "if", "then", "than", "too", "very", "just", "about", "up", "out",
    "get", "got", "go", "going", "gone", "come", "came", "take", "took",
    "make", "made", "see", "saw", "know", "knew", "think", "thought",
    "want", "need", "like", "look", "find", "give", "tell", "work",
    "try", "use", "put", "say", "said", "的", "了", "在", "是", "我",
    "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很",
    "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己",
    "这", "他", "她", "它", "吗", "吧", "呢", "啊", "哦", "嗯",
}


def load_signals(db_path: Path) -> list[dict]:
    """从 SQLite 加载所有信号"""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT id, source, signal_type, title, content, url, author,
               score, score_label, posted_at, keywords, category, geo,
               metadata, collected_at
        FROM demand_signals
        ORDER BY score DESC
    """).fetchall()
    conn.close()

    signals = []
    for row in rows:
        d = dict(row)
        # 解析 JSON 字段
        for key in ("keywords", "metadata"):
            if d.get(key):
                try:
                    d[key] = json.loads(d[key])
                except (json.JSONDecodeError, TypeError):
                    d[key] = [] if key == "keywords" else {}
            else:
                d[key] = [] if key == "keywords" else {}
        signals.append(d)
    return signals


def extract_keywords(text: str) -> set[str]:
    """从文本中提取有意义的关键词（小写、去停用词、去短词）"""
    if not text:
        return set()
    # 保留中文词组（2-8字）和英文单词（3+字母）
    words = set()

    # 英文单词
    en_words = re.findall(r'[a-z][a-z0-9_]+', text.lower())
    words.update(w for w in en_words if w not in STOPWORDS and len(w) >= 3)

    # 中文词组（简单 2-4 滑动窗口）
    cn_chars = re.findall(r'[\u4e00-\u9fff]+', text)
    for segment in cn_chars:
        for length in (2, 3, 4):
            for i in range(len(segment) - length + 1):
                word = segment[i:i + length]
                if word not in STOPWORDS:
                    words.add(word)

    return words


def cluster_signals(signals: list[dict]) -> list[dict]:
    """
    聚类算法：
    1. 先按 (source, signal_type, category) 粗分桶
    2. 在每个桶内，按关键词重叠度合并成聚类
    3. 计算每个聚类的综合得分
    """
    # ── 第一步：粗分桶 ──────────────────────────────────────────────
    buckets = defaultdict(list)
    for sig in signals:
        # 标准化 category
        cat = (sig.get("category") or "uncategorized").strip() or "uncategorized"
        sig_type = (sig.get("signal_type") or "discussion").strip()
        bucket_key = (sig_type, cat)
        buckets[bucket_key].append(sig)

    # ── 第二步：桶内关键词聚类 ──────────────────────────────────────
    clusters = []

    for (sig_type, category), bucket_sigs in buckets.items():
        if len(bucket_sigs) < 2:
            continue

        # 提取每条信号的关键词
        sig_keywords = []
        for sig in bucket_sigs:
            text = f"{sig.get('title', '')} {sig.get('content', '')}"
            kws = extract_keywords(text)
            # 加入 metadata 中的 subreddit 等标签
            meta = sig.get("metadata", {})
            if isinstance(meta, dict):
                for key in ("subreddit", "source_detail"):
                    val = meta.get(key, "")
                    if val:
                        kws.add(val.lower().replace("r/", ""))
            sig_keywords.append((sig, kws))

        # 简单聚类：按 top 关键词合并
        # 统计桶内所有关键词频率
        all_kws = Counter()
        for _, kws in sig_keywords:
            all_kws.update(kws)

        # 取 top-N 关键词作为聚类种子
        top_kws = [kw for kw, _ in all_kws.most_common(50)]

        # 按种子关键词分组
        seed_groups = defaultdict(list)
        for sig, kws in sig_keywords:
            matched = False
            for seed in top_kws:
                if seed in kws:
                    seed_groups[seed].append(sig)
                    matched = True
                    break
            if not matched:
                seed_groups["_other"].append(sig)

        # 为每个种子组生成聚类
        for seed, group_sigs in seed_groups.items():
            if len(group_sigs) < 2:
                continue

            # 聚类元数据
            sources = Counter(s["source"] for s in group_sigs)
            total_score = sum(s.get("score", 0) or 0 for s in group_sigs)
            avg_score = total_score / len(group_sigs) if group_sigs else 0

            # 跨平台多样性得分 (Shannon entropy normalized)
            source_counts = list(sources.values())
            total = sum(source_counts)
            diversity = 0.0
            if total > 0:
                import math
                for c in source_counts:
                    p = c / total
                    if p > 0:
                        diversity -= p * math.log2(p)
                # normalize: max diversity = log2(num_unique_sources)
                max_div = math.log2(max(len(sources), 1))
                diversity = diversity / max_div if max_div > 0 else 0

            # 时间新鲜度（最近 7 天内的信号占比）
            recent_count = 0
            for s in group_sigs:
                posted = s.get("posted_at") or s.get("collected_at")
                if posted:
                    try:
                        ts = datetime.fromisoformat(posted.replace("Z", "+00:00"))
                        age_days = (datetime.now(ts.tzinfo) - ts).days
                        if age_days <= 7:
                            recent_count += 1
                    except Exception:
                        pass
            freshness = recent_count / len(group_sigs) if group_sigs else 0

            # 综合机会得分
            # 公式：信号量 × log(总热度+1) × (1 + 跨平台多样性) × (1 + 新鲜度)
            import math
            opportunity_score = (
                len(group_sigs)
                * math.log2(total_score + 2)
                * (1 + diversity)
                * (1 + freshness)
            )

            # 代表性标题（取 score 最高的 3 个）
            top_sigs = sorted(group_sigs, key=lambda s: s.get("score", 0) or 0, reverse=True)[:3]
            representative_titles = [s.get("title", "")[:80] for s in top_sigs if s.get("title")]

            # 关键词标签
            group_kws = Counter()
            for s in group_sigs:
                text = f"{s.get('title', '')} {s.get('content', '')}"
                group_kws.update(extract_keywords(text))
            top_keywords = [kw for kw, _ in group_kws.most_common(10)]

            clusters.append({
                "seed_keyword": seed,
                "signal_type": sig_type,
                "category": category,
                "signal_count": len(group_sigs),
                "sources": dict(sources.most_common()),
                "source_diversity": round(diversity, 3),
                "total_score": round(total_score, 1),
                "avg_score": round(avg_score, 1),
                "freshness_7d": round(freshness, 3),
                "opportunity_score": round(opportunity_score, 2),
                "top_keywords": top_keywords,
                "representative_titles": representative_titles,
                "sample_urls": [s.get("url", "") for s in top_sigs[:2] if s.get("url")],
            })

    # 按机会得分排序
    clusters.sort(key=lambda c: c["opportunity_score"], reverse=True)
    return clusters


def print_report(clusters: list[dict], top_n: int = 30, min_signals: int = 3):
    """打印人类可读的聚类报告"""
    filtered = [c for c in clusters if c["signal_count"] >= min_signals]
    top_clusters = filtered[:top_n]

    print("=" * 72)
    print(f"  📊 需求信号聚合分析报告")
    print(f"  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  聚类总数: {len(filtered)} (≥{min_signals}条信号)")
    print("=" * 72)
    print()

    for i, c in enumerate(top_clusters, 1):
        # 来源标签
        source_tags = " ".join(f"[{s}×{n}]" for s, n in c["sources"].items())

        # 新鲜度指示
        fresh = "🔥" if c["freshness_7d"] > 0.5 else "🕐" if c["freshness_7d"] > 0.1 else "❄️"

        # 多样性指示
        div = "🌐" if c["source_diversity"] > 0.5 else "📌"

        print(f"#{i:2d}  {fresh}{div} 机会分 {c['opportunity_score']:>8.1f}  "
              f"|  {c['signal_count']:>3}条信号  |  {c['signal_type']}")
        print(f"    类别: {c['category']}")
        print(f"    来源: {source_tags}")
        print(f"    关键词: {', '.join(c['top_keywords'][:6])}")
        if c["representative_titles"]:
            print(f"    示例: {c['representative_titles'][0]}")
        if c["sample_urls"]:
            print(f"    链接: {c['sample_urls'][0]}")
        print()

    # ── 汇总统计 ────────────────────────────────────────────────────
    print("-" * 72)
    print("📈 来源分布汇总:")
    all_sources = Counter()
    for c in filtered:
        for src, cnt in c["sources"].items():
            all_sources[src] += cnt
    for src, cnt in all_sources.most_common():
        bar = "█" * min(cnt // 5, 40)
        print(f"  {src:<20} {cnt:>4}  {bar}")
    print()


def print_json(clusters: list[dict], min_signals: int = 3):
    """JSON 格式输出"""
    filtered = [c for c in clusters if c["signal_count"] >= min_signals]
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_clusters": len(filtered),
        "clusters": filtered,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate sparse demand signals into opportunity clusters"
    )
    parser.add_argument("--top", type=int, default=30, help="Show top N clusters (default: 30)")
    parser.add_argument("--min", type=int, default=3, help="Min signals per cluster (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--db", type=str, default=str(DB_PATH), help="Path to demand_signals.db")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    signals = load_signals(db_path)
    if not signals:
        print("⚠️  No signals found in database.", file=sys.stderr)
        sys.exit(0)

    print(f"📥 Loaded {len(signals)} signals from {db_path}", file=sys.stderr)

    clusters = cluster_signals(signals)
    print(f"🔍 Found {len(clusters)} clusters (≥{args.min} signals)", file=sys.stderr)

    if args.json:
        print_json(clusters, min_signals=args.min)
    else:
        print_report(clusters, top_n=args.top, min_signals=args.min)


if __name__ == "__main__":
    main()
