"""broad_reddit.py — Wide-net Reddit search across all subreddits.

Uses Reddit search (not subreddit-specific) to surface scattered
demand signals from dozens of niche communities.

Strategy:
    6 search queries × 100 posts = up to 600 posts/run
    Covers 100+ subreddits — each sub has ~1 post (noise alone)
    Aggregate mentions across subs = strong demand signal

Cost: 600 × $0.00115 = ~$0.70/run
"""

import json
import time
import sys
import os
from collections import Counter

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

from base import BaseCollector
import config


class BroadRedditCollector(BaseCollector):
    """Wide-net Reddit search collector — 6 queries, up to 600 posts."""
    
    name = "reddit_broad"
    
    def __init__(self, cfg):
        super().__init__(cfg)
        self.apify_token = getattr(cfg, "APIFY_API_TOKEN", "") or os.environ.get("APIFY_API_TOKEN", "")
        self.actor_id = getattr(cfg, "APIFY_REDDIT_ACTOR", "automation-lab/reddit-scraper")
        self.max_per_query = getattr(cfg, "BROAD_MAX_PER_QUERY", 100)
        self.delay = getattr(cfg, "REDDIT_DELAY_BETWEEN_CALLS", 30)
        self._client = None
    
    def _log(self, msg):
        print(msg)
    
    @property
    def client(self):
        if self._client is None:
            from apify_client import ApifyClient
            self._client = ApifyClient(self.apify_token)
        return self._client
    
    def _build_search_urls(self):
        """6 search demand-discovery search queries covering product/pain/alternative angles."""
        queries = [
            # Product-seeking
            '"looking for" product OR tool OR service OR app',
            # Alternative/replacement
            '"alternative to" OR "instead of" OR "replacement for" product OR service',
            # Pain/frustration
            '"I wish there was" OR "I hate when" product OR tool',
            # E-commerce specific
            'amazon FBA product idea OR trending OR private label OR sourcing',
            # Lifestyle/pets/home (broad demand)
            'pet OR dog OR cat OR garden OR home product OR supply OR solution',
            # SaaS/tools (digital products)
            'software OR app OR SaaS OR tool recommendation',
        ]
        urls = []
        for q in queries:
            urls.append(f"https://www.reddit.com/search/?q={q}&sort=new&t=week")
        return urls
    
    def collect(self):
        """Run 6 search queries, each 100 posts. Return list of signal dicts."""
        all_signals = []
        urls = self._build_search_urls()
        
        self._log(f"  Actor: {self.actor_id}")
        self._log(f"  Queries: {len(urls)} (max {self.max_per_query} posts each = up to {len(urls)*self.max_per_query} posts)")
        
        for i, url in enumerate(urls, 1):
            self._log(f"\n  [{i}/{len(urls)}] Search: {url.split('q=')[-1].split('&')[0][:50]}...")
            
            if i > 1:
                time.sleep(self.delay)
            
            run_input = {
                "startUrls": [{"url": url}],
                "maxPostsPerSource": self.max_per_query,
                "includeComments": False,
            }
            
            # Call Actor with retry
            run = None
            for attempt in range(1, 3):
                try:
                    run = self.client.actor(self.actor_id).call(run_input=run_input)
                    if run.status == "SUCCEEDED":
                        break
                    self._log(f"    Attempt {attempt}: status={run.status}")
                except Exception as e:
                    self._log(f"    Attempt {attempt} error: {e}")
                    if attempt < 1:
                        time.sleep(20)
            
            if not run or run.status != "SUCCEEDED":
                self._log(f"    ✗ Failed, skipping")
                continue
            
            # Fetch results
            try:
                dataset_id = getattr(run, "default_dataset_id", None) or getattr(run, "defaultDatasetId", None)
                if not dataset_id:
                    continue
                dataset = self.client.dataset(dataset_id)
            except Exception as e:
                self._log(f"    ✗ Dataset error: {e}")
                continue
            
            new_count = 0
            for item in dataset.iterate_items():
                if item.get("type") != "post":
                    continue
                
                signal = self._make_signal(item)
                if signal:
                    all_signals.append(signal)
                    new_count += 1
            
            self._log(f"    ✓ {new_count} new posts")
        
        self._log(f"\n  Total new: {len(all_signals)} posts from {len(urls)} queries")
        return all_signals
    
    def _make_signal(self, item):
        """Convert Apify item to signal dict. Returns None if should skip."""
        title = item.get("title", "").strip()
        if not title:
            return None
        
        url = item.get("url", "")
        subreddit = item.get("subreddit", "").strip()
        
        meta = {
            "subreddit": f"r/{subreddit}",
            "source_detail": "Broad search via Apify",
            "comments": item.get("numComments", 0),
            "ups": item.get("score", 0),
            "upvoteRatio": item.get("upvoteRatio"),
            "author": item.get("author", ""),
            "permalink": item.get("permalink", ""),
            "domain": item.get("domain", ""),
            "selftext": item.get("selfText", "")[:500],
            "isVideo": item.get("isVideo", False),
            "isNSFW": item.get("isNSFW", False),
        }
        
        # Improved signal type detection
        t = title.lower()
        if any(w in t for w in ["wish there was","wish there were"]):
            sig_type = "feature_request"
        elif any(w in t for w in ["looking for","recommend","suggestion","need","want","where can i","where to","anyone know"]):
            sig_type = "purchase_intent"
        elif any(w in t for w in ["alternative","instead of","replacement","better than","vs","comparison"]):
            sig_type = "pain_point"
        elif any(w in t for w in ["trending","best seller","winning product","hot product","trend","popular"]):
            sig_type = "trend"
        elif any(w in t for w in ["hate","angry","frustrated","annoying","broken","worst","terrible","awful","never again"]):
            sig_type = "pain_point"
        else:
            sig_type = "discussion"
        
        return self.make_signal(
            signal_type=sig_type,
            title=title,
            content=item.get("selfText", "")[:500],
            url=url,
            author=item.get("author", ""),
            score=item.get("numComments", 0),  # Use numComments since score=0
            score_label="comments",
            posted_at=item.get("createdAt"),
            keywords=[subreddit, sig_type],
            category=f"r/{subreddit}",
            metadata=meta,
        )
