"""Reddit collector — v6 Apify-powered, one-subreddit-per-call.

Uses Apify Reddit Scraper Actor ($0.00115/post on FREE tier).
Apify handles proxy rotation, anti-bot bypass, and parsing.

Chain:
  1. For each subreddit, call Apify Actor with single subreddit URL
  2. Actor scrapes Reddit using Apify's proxy infrastructure
  3. Fetch results from Apify Dataset API for that run
  4. Build signal dicts directly

Why v6 works when v5 failed:
  - Reddit RSS rate limits are ~100 req/min per IP range
  - Running 9 subreddits in ONE Actor call overwhelms RSS with concurrent fetches
  - Solution: one subreddit per Actor call, 30s delay between calls
  - Each call gets its own fresh IP from Apify's pool, avoiding shared rate limits
  - If one call fails (RSS 429), only that subreddit is lost, not the whole batch

Cost management:
  - 9 subreddits × 25 posts = 225 posts/day
  - 225 × $0.00115 = $0.26/day = ~$7.80/month
  - Plus ~4.5 min total runtime due to delays (9 × 30s)
"""

import os
import time
from datetime import datetime

from base import BaseCollector
import config


class RedditCollector(BaseCollector):
    name = "reddit"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.apify_token = getattr(cfg, "APIFY_API_TOKEN", "") or os.environ.get("APIFY_API_TOKEN", "")
        self.actor_id = getattr(cfg, "APIFY_REDDIT_ACTOR", "automation-lab/reddit-scraper")
        self.subreddits = getattr(cfg, "REDDIT_SUBREDDITS", [])
        self.per_sub = getattr(cfg, "REDDIT_PER_SUBREDDIT", 25)
        self.max_age_hours = getattr(cfg, "REDDIT_MAX_AGE_HOURS", 24)
        self.delay_between_calls = getattr(cfg, "REDDIT_DELAY_BETWEEN_CALLS", 30)
        self._client = None

    def _log(self, msg):
        print(msg)

    @property
    def client(self):
        if self._client is None:
            from apify_client import ApifyClient
            self._client = ApifyClient(self.apify_token)
        return self._client

    def collect(self) -> list:
        """Run Apify Actor per-subreddit to avoid RSS rate limits."""
        all_signals = []
        total_skipped = 0

        self._log(f"  Actor: {self.actor_id}")
        self._log(f"  Subreddits: {len(self.subreddits)} (one call per subreddit, {self.delay_between_calls}s delay)")

        for i, subreddit in enumerate(self.subreddits, 1):
            self._log(f"\n  [{i}/{len(self.subreddits)}] r/{subreddit}...")

            # Delay between calls (skip first)
            if i > 1:
                time.sleep(self.delay_between_calls)

            # Single-subreddit Actor input
            # V7 fix: includeComments=True to get selfText + top comment
            run_input = {
                "startUrls": [{"url": f"https://www.reddit.com/r/{subreddit}/new/"}],
                "maxPostsPerSource": self.per_sub,
                "includeComments": True,
                "maxCommentsPerPost": 2,
                "commentDepth": 1,
            }

            # Call Actor with retry (Run is pydantic BaseModel, not dict)
            max_retries = 2
            run = None
            for attempt in range(1, max_retries + 1):
                try:
                    run = self.client.actor(self.actor_id).call(run_input=run_input)
                    if run.status == "SUCCEEDED":
                        break
                    else:
                        self._log(f"    Attempt {attempt}: status={run.status}")
                except Exception as e:
                    self._log(f"    Attempt {attempt} error: {e}")
                    if attempt < max_retries:
                        time.sleep(20)

            if not run or run.status != "SUCCEEDED":
                self._log(f"    ✗ Failed after {max_retries} attempts, skipping")
                continue

            # Fetch results from Dataset
            try:
                # apify-client 3.x: snake_case; older xDs: camelCase fallback
                dataset_id = getattr(run, "default_dataset_id", None) or getattr(run, "defaultDatasetId", None)
                if not dataset_id:
                    self._log(f"    ✗ No dataset_id")
                    continue
                dataset = self.client.dataset(dataset_id)
            except Exception as e:
                self._log(f"    ✗ Dataset open failed: {e}")
                continue

            sub_signals = []
            skipped = 0
            for item in dataset.iterate_items():
                if self.max_age_hours and item.get("createdAt"):
                    try:
                        created = datetime.fromisoformat(item["createdAt"].replace("Z", "+00:00"))
                        age_hours = (datetime.now(created.tzinfo) - created).total_seconds() / 3600
                        if age_hours > self.max_age_hours:
                            skipped += 1
                            continue
                    except Exception:
                        pass
                sub_signals.append(self._make_signal(item))

            all_signals.extend(sub_signals)
            total_skipped += skipped
            self._log(f"    ✓ {len(sub_signals)} signals (skipped {skipped} stale)")

        self._log(f"\n  Total: {len(all_signals)} signals (skipped {total_skipped} stale)")
        return all_signals

    def _make_signal(self, item: dict) -> dict:
        """Convert Apify item to our signal format."""
        title = item.get("title", "").lower()
        url = item.get("url", f"https://www.reddit.com{item.get('permalink', '')}")
        subreddit = item.get("subreddit", "")

        # Determine signal type
        if any(w in title for w in ["wish there was", "looking for alternative", "not satisfied"]):
            sig_type = "pain_point"
        elif any(w in title for w in ["where can i buy", "where to source", "where to find"]):
            sig_type = "purchase_intent"
        elif any(w in title for w in ["trending", "best seller", "winning product", "hot product"]):
            sig_type = "trend"
        elif any(w in title for w in ["product idea", "what to sell", "what should i sell"]):
            sig_type = "feature_request"
        elif any(w in title for w in ["pain point", "struggle", "challenge", "frustrated"]):
            sig_type = "pain_point"
        else:
            sig_type = "discussion"

        score = item.get("score", 0) or 0
        score_label = "score" if score > 0 else "comments"

        meta = {
            "subreddit": f"r/{subreddit}",
            "source_detail": "Apify Reddit Scraper Actor",
            "comments": item.get("numComments", 0),
            "ups": item.get("score", 0),
            "upvoteRatio": item.get("upvoteRatio"),
            "author": item.get("author", ""),
            "permalink": item.get("permalink", ""),
            "domain": item.get("domain", ""),
            "selftext": item.get("selfText", "")[:500],
            "isVideo": item.get("isVideo", False),
            "isNSFW": item.get("isNSFW", False),
            "totalAwards": item.get("totalAwards", 0),
            "subredditSubscribers": item.get("subredditSubscribers"),
            "thumbnail": item.get("thumbnail", ""),
        }

        return self.make_signal(
            signal_type=sig_type,
            title=item.get("title", ""),
            content=item.get("selfText", "")[:500],
            url=url,
            author=item.get("author", ""),
            score=score if score > 0 else item.get("numComments", 0),
            score_label=score_label,
            posted_at=item.get("createdAt"),
            keywords=[subreddit, sig_type],
            category=f"r/{subreddit}",
            metadata=meta,
        )
