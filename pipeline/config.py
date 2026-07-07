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

# Reddit search query templates (Google site:reddit.com)
REDDIT_QUERIES = [
    '"I wish there was" product',
    '"where can I buy" OR "does anyone know where to find"',
    '"trending product" OR "best seller" ecommerce',
    '"what should I sell" OR "product idea" dropship amazon',
    '"not satisfied with" OR "looking for alternative" product',
    '"anyone tried" OR "product recommendation"',
]

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
