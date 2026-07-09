#!/usr/bin/env python3
"""
Pipeline Orchestrator — runs all data source collectors and stores signals.

Usage:
    python3 run.py                    # Run ALL collectors
    python3 run.py --only hn github   # Run specific collectors only
    python3 run.py --stats            # Show database stats only
    python3 run.py --skip reddit      # Skip specific collectors

Collector names: amazon, trustpilot, producthunt, hackernews, github,
                 google_trends, youtube, tiktok, reddit, amz_dataset
"""
import sys
import os
import time
import argparse
from datetime import datetime

# Setup paths
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPELINE_DIR)
sys.path.insert(0, os.path.join(PIPELINE_DIR, "collectors"))

import config
from db import Database
from base import BaseCollector


# ── Collector registry ─────────────────────────────────────────────────
COLLECTOR_MAP = {
    "hackernews":    ("hackernews.HackerNewsCollector", "Hacker News"),
    "github":        ("github_issues.GitHubIssuesCollector", "GitHub Issues"),
    "google_trends": ("google_trends.GoogleTrendsCollector", "Google Trends"),
    "youtube":       ("youtube.YouTubeCollector", "YouTube"),
    "tiktok":        ("tiktok.TikTokCollector", "TikTok"),
    "amazon":        ("amazon.AmazonCollector", "Amazon"),
    "trustpilot":    ("trustpilot.TrustpilotCollector", "Trustpilot"),
    "producthunt":   ("producthunt.ProductHuntCollector", "Product Hunt"),
    "amz_dataset":   ("amz_dataset.AmazonDatasetCollector", "Amazon Dataset"),
    "reddit":        ("reddit.RedditCollector", "Reddit (via Apify)"),
    "reddit_broad":  ("broad_reddit.BroadRedditCollector", "Reddit Broad (all subs)"),
}


def load_collector(name: str, cfg):
    """Dynamically import and instantiate a collector."""
    module_path, display_name = COLLECTOR_MAP[name]
    module_name, class_name = module_path.rsplit(".", 1)
    mod = __import__(module_name)
    cls = getattr(mod, class_name)
    return cls(cfg), display_name


def run_collector(name: str, cfg, db: Database) -> dict:
    """Run a single collector and store results."""
    try:
        collector, display_name = load_collector(name, cfg)
    except Exception as e:
        return {"name": name, "status": "failed", "error": f"Import failed: {e}",
                "new": 0, "dup": 0}

    print(f"\n{'='*60}")
    print(f"  [{name}] {display_name}")
    print(f"{'='*60}")

    start = time.time()
    signals, errors = collector.run()
    elapsed = time.time() - start

    if errors:
        for err in errors[:3]:
            print(f"  ERROR: {err[:200]}")

    if not signals:
        print(f"  No signals collected ({elapsed:.1f}s)")
        db.log_run(name, "failed", 0, 0, error="No signals collected",
                   metadata={"elapsed": elapsed})
        return {"name": name, "status": "failed", "error": "No signals",
                "new": 0, "dup": 0}

    new_count, dup_count = db.insert_signals(signals)
    print(f"  Collected: {len(signals)} signals | New: {new_count} | Duplicates: {dup_count} | {elapsed:.1f}s")

    db.log_run(name, "success", new_count, dup_count,
               metadata={"total_collected": len(signals), "elapsed": elapsed})

    return {"name": name, "status": "success", "new": new_count, "dup": dup_count,
            "total": len(signals), "elapsed": elapsed}


def print_stats(db: Database):
    """Print database statistics."""
    stats = db.get_stats()
    print(f"\n{'='*60}")
    print(f"  DATABASE STATISTICS")
    print(f"{'='*60}")
    print(f"  Total signals: {stats['total']}")
    print(f"\n  By source:")
    for source, count in stats["by_source"].items():
        print(f"    {source:20s} {count:6d}")
    print(f"\n  By signal type:")
    for stype, count in stats["by_type"].items():
        print(f"    {stype:20s} {count:6d}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Cross-border e-commerce demand signal pipeline")
    parser.add_argument("--only", nargs="+", help="Run only these collectors")
    parser.add_argument("--skip", nargs="+", help="Skip these collectors")
    parser.add_argument("--stats", action="store_true", help="Show database stats only")
    parser.add_argument("--daily", action="store_true",
                        help="Reddit daily mode: past-24h window, newest-first sort")
    parser.add_argument("--reddit-tbs", default=None,
                        help="Override Reddit Google time window (e.g. qdr:d, qdr:w)")
    parser.add_argument("--deep", action="store_true",
                        help="Reddit: deep-fetch each post's .json for real created_utc/upvotes")
    parser.add_argument("--fetch-mode", choices=["auto", "browser", "http"], default=None,
                        help="Reddit: fetch mode — auto (default), browser (BrowserAct only), http (direct)")
    args = parser.parse_args()

    # Apply Reddit daily / override knobs BEFORE collectors are instantiated.
    if args.daily:
        config.REDDIT_TBS = "qdr:d"
        config.REDDIT_SORT = "sbd:1"
    if args.reddit_tbs:
        config.REDDIT_TBS = args.reddit_tbs
    if args.deep:
        config.REDDIT_DEEP_FETCH = True
    if args.fetch_mode:
        config.REDDIT_FETCH_MODE = args.fetch_mode

    db = Database(config.DB_PATH, config.SCHEMA_PATH)

    if args.stats:
        print_stats(db)
        return

    # Determine which collectors to run
    if args.only:
        run_list = [c for c in COLLECTOR_MAP if c in args.only]
    else:
        run_list = list(COLLECTOR_MAP.keys())

    if args.skip:
        run_list = [c for c in run_list if c not in args.skip]

    print(f"\n{'#'*60}")
    print(f"  DEMAND SIGNAL PIPELINE")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"  Collectors: {', '.join(run_list)}")
    print(f"  Database: {config.DB_PATH}")
    print(f"{'#'*60}\n")

    pipeline_start = time.time()
    results = []

    for name in run_list:
        result = run_collector(name, config, db)
        results.append(result)

    # Summary
    total_elapsed = time.time() - pipeline_start
    total_new = sum(r.get("new", 0) for r in results)
    total_dup = sum(r.get("dup", 0) for r in results)
    success_count = sum(1 for r in results if r["status"] == "success")
    fail_count = sum(1 for r in results if r["status"] == "failed")

    print(f"\n{'#'*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Success: {success_count}/{len(results)} | Failed: {fail_count}")
    print(f"  Total new signals: {total_new} | Duplicates: {total_dup}")
    print(f"  Total time: {total_elapsed:.1f}s")
    print(f"{'#'*60}\n")

    print_stats(db)


if __name__ == "__main__":
    main()
