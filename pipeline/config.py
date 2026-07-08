"""
Pipeline configuration — all paths, settings, and defaults.
"""
import os

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.join(PROJECT_ROOT, "pipeline")
TOOLS_DIR    = os.path.join(PROJECT_ROOT, "tools")

# Database
DB_PATH = os.path.join(PIPELINE_DIR, "demand_signals.db")
SCHEMA_PATH = os.path.join(PIPELINE_DIR, "schema.sql")

# BrowserAct
BROWSERACT_BIN = os.path.expanduser("~/.local/bin/browser-act")
BROWSERACT_DATA_DIR = os.path.join(PROJECT_ROOT, "..", ".workbuddy", "browseract")
BROWSERACT_BROWSER_ID = "105745062293719635"  # reddit-research stealth browser

# Python env
PYTHON_BIN = os.path.expanduser("~/.workbuddy/binaries/python/envs/cross-border/bin/python3")

# ── Research keywords ──────────────────────────────────────────────────
# Default search terms for cross-border e-commerce demand discovery
DEFAULT_KEYWORDS = [
    "amazon fba product research",
    "what should I sell on amazon",
    "dropshipping product ideas 2025",
    "best products to sell online",
    "trending products ecommerce",
    "product gap market opportunity",
]

# ── Reddit daily-scrape tuning ────────────────────────────────────────
# Time window passed to Google (tbs). Daily cron should use qdr:d (past 24h).
# Use qdr:w (past week) for catch-up / backfill runs. Override per-run with
# `python3 run.py --only reddit --reddit-tbs qdr:w` or the --daily flag.
REDDIT_TBS = "qdr:d"
# Sort results newest-first so the freshest posts surface on top.
REDDIT_SORT = "sbd:1"
# Deep-fetch each new post's old.reddit .json to recover the REAL created_utc
# + upvotes + num_comments. Costs ~1.5s/post — v3: ON by default for daily runs.
REDDIT_DEEP_FETCH = True
# Deep-fetch budget: top-K most-commented posts per query (bounds runtime).
REDDIT_TOP_K = 5
# Drop posts older than this many hours based on recovered posted_at.
# v3: 24h default — daily runs should only keep fresh posts.
REDDIT_MAX_AGE_HOURS = 24
# Fetch mode: 'auto' (try HTTP first, then BrowserAct), 'browser' (BrowserAct only),
# 'http' (curl_cffi/urllib only — faster but may get blocked by Google).
REDDIT_FETCH_MODE = "auto"

# ── Reddit API credentials (Developer Platform paid API) ───────────
# Register at https://developers.reddit.com → create app → get client_id + secret
# Cost: $0.24 / 1000 requests. Direct HTTP to oauth.reddit.com — no proxy/BrowserAct needed.
REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""
REDDIT_USER_AGENT = "business-radar/1.0 by vibe-coding"

# Apify (Reddit scraping via Apify platform)
# Loaded from environment — never hardcode secrets
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
APIFY_REDDIT_ACTOR = os.environ.get("APIFY_REDDIT_ACTOR", "automation-lab/reddit-scraper")

# ── Reddit daily-scrape tuning (official API mode) ───────────────────
# List of subreddits to monitor (direct .json API calls — no search engine needed)
REDDIT_SUBREDDITS = [
    "AmazonFBA",
    "ecommerce",
    "dropshipping",
    "FulfillmentByAmazon",
    "AmazonSeller",
    "smallbusiness",
    "Entrepreneur",
    "EtsyCommunity",
    "shopify",
]

# Max posts per subreddit per day
REDDIT_PER_SUBREDDIT = 25

# Delay between Apify Actor calls (avoids Reddit RSS rate limits)
REDDIT_DELAY_BETWEEN_CALLS = 30

# Reddit search query templates (Google site:reddit.com)
# ── Two-tier strategy: broad discovery + targeted e-commerce ──────────
# Tier 1: e-commerce focused subreddits (high signal, low noise)
REDDIT_QUERIES_EC = [
    'site:reddit.com/r/ecommerce+shopify+dropshipping+FulfillmentByAmazon+AmazonSeller "product idea" OR "what to sell" OR "trending"',
    'site:reddit.com/r/ecommerce+smallbusiness+Entrepreneur "looking for supplier" OR "where to source" OR "best product to sell"',
    'site:reddit.com/r/AmazonSeller+FulfillmentByAmazon+amazon "not satisfied with" OR "looking for alternative" OR "wish there was"',
    'site:reddit.com/r/dropshipping+ecommerce+shopify "anyone tried" OR "product recommendation" OR "winning product"',
    'site:reddit.com/r/ecommerce+smallbusiness "pain point" OR "struggle with" OR "biggest challenge"',
]
# Tier 2: broader demand signals across all of reddit (higher noise, catches niche gaps)
REDDIT_QUERIES_BROAD = [
    '"I wish there was a" product OR tool OR app OR service',
    '"looking for alternative" product OR tool OR service',
    '"where can I buy" product OR gift OR supply',
    '"not satisfied with" product OR brand OR purchase',
]
# Combined (default): Tier 1 first, then Tier 2
REDDIT_QUERIES = REDDIT_QUERIES_EC + REDDIT_QUERIES_BROAD

# GitHub issue search queries
GITHUB_QUERIES = [
    'label:enhancement label:"feature request" state:open',
    'label:wishlist state:open',
    'label:enhancement "amazon fba" OR "ecommerce" OR "dropshipping"',
]

# Amazon product search keywords
AMAZON_SEARCH_KEYWORDS = [
    "best seller 2025",
    "trending products",
    "new arrivals popular",
]

# Trustpilot categories
TRUSTPILOT_CATEGORIES = [
    "amazon.com",
    "aliexpress.com",
    "temu.com",
    "shein.com",
]

# Google Trends keywords
TRENDS_KEYWORDS = [
    "amazon fba",
    "dropshipping",
    "shopify",
    "what to sell on amazon",
    "ecommerce trends 2025",
]

# Amazon dataset categories (HuggingFace McAuley-Lab)
AMZ_DATASET_CATEGORIES = ["All_Beauty"]
AMZ_DATASET_SAMPLE_SIZE = 500  # reviews to sample per category

# ── Rate limits ────────────────────────────────────────────────────────
RATE_LIMITS = {
    "hackernews": 0.5,    # 2 req/s (Firebase is generous)
    "github": 0.17,       # ~10 req/min unauthenticated
    "google_trends": 1.0, # 1 req/s (conservative)
    "youtube": 1.0,       # conservative
    "tiktok": 2.0,       # conservative
    "amazon": 2.0,       # 1 req per 2s (avoid blocks)
    "trustpilot": 1.0,
    "producthunt": 1.0,
    "reddit": 3.0,       # BrowserAct is slow, 1 req per 3s
}
