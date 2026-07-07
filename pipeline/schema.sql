-- ============================================================
-- Cross-Border E-commerce Demand Signal Database Schema
-- ============================================================

-- Main signal table: all demand signals from all sources
CREATE TABLE IF NOT EXISTS demand_signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,          -- amazon, reddit, hackernews, github, google_trends, youtube, tiktok, trustpilot, producthunt, amz_dataset
    signal_type     TEXT NOT NULL,          -- pain_point, purchase_intent, trend, feature_request, review, discussion, product_listing, video_content
    title           TEXT,
    content         TEXT,                   -- summary, review text, description
    url             TEXT,
    author          TEXT,
    score           REAL,                   -- upvotes, rating, comment count, search volume
    score_label     TEXT,                   -- 'upvotes', 'rating', 'comments', 'search_volume'
    posted_at       TEXT,                   -- ISO timestamp when signal was posted
    keywords        TEXT,                   -- JSON array of extracted keywords
    category        TEXT,                   -- product category
    geo             TEXT,                   -- geographic signal (US, EU, etc.)
    metadata        TEXT,                   -- JSON for source-specific fields
    collected_at    TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source, url)                     -- dedup: same source + URL = skip
);

-- Collection run log: track each pipeline execution
CREATE TABLE IF NOT EXISTS collection_runs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    source              TEXT NOT NULL,
    status              TEXT NOT NULL,      -- success, failed, partial
    signals_collected   INTEGER DEFAULT 0,
    signals_duplicated  INTEGER DEFAULT 0,
    error               TEXT,
    started_at          TEXT NOT NULL,
    finished_at         TEXT,
    metadata            TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_signals_source ON demand_signals(source);
CREATE INDEX IF NOT EXISTS idx_signals_type ON demand_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_score ON demand_signals(score DESC);
CREATE INDEX IF NOT EXISTS idx_signals_posted ON demand_signals(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_category ON demand_signals(category);
