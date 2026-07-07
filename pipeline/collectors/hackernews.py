"""Hacker News collector — Firebase API (no key needed)."""
import requests
from datetime import datetime

from base import BaseCollector
import config


class HackerNewsCollector(BaseCollector):
    name = "hackernews"

    BASE = "https://hacker-news.firebaseio.com/v0"

    def _get_item(self, item_id: int) -> dict:
        r = requests.get(f"{self.BASE}/item/{item_id}.json", timeout=10)
        return r.json() if r.status_code == 200 else {}

    def _classify(self, title: str) -> str:
        """Classify HN post into signal type."""
        t = title.lower()
        if any(w in t for w in ["ask hn", "what do you use", "recommend"]):
            return "purchase_intent"
        if any(w in t for w in ["show hn", "launched", "built"]):
            return "product_listing"
        if any(w in t for w in ["trend", "2025", "2024", "future of"]):
            return "trend"
        return "discussion"

    def collect(self) -> list:
        all_signals = []

        # 1. Top stories
        r = requests.get(f"{self.BASE}/topstories.json", timeout=10)
        if r.status_code != 200:
            return all_signals
        top_ids = r.json()[:30]

        for sid in top_ids:
            item = self._get_item(sid)
            if not item or not item.get("title"):
                continue

            score = item.get("score", 0)
            comments = item.get("descendants", 0)
            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={sid}")

            all_signals.append(self.make_signal(
                signal_type=self._classify(title),
                title=title,
                content="",
                url=url,
                author=item.get("by", ""),
                score=score,
                score_label="upvotes",
                posted_at=datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
                metadata={"hn_id": sid, "comments": comments, "type": item.get("type", "")},
            ))
            self.sleep(self.config.RATE_LIMITS["hackernews"])

        # 2. Ask HN (questions = purchase intent signals)
        r2 = requests.get(f"{self.BASE}/askstories.json", timeout=10)
        if r2.status_code == 200:
            ask_ids = r2.json()[:15]
            for sid in ask_ids:
                item = self._get_item(sid)
                if not item or not item.get("title"):
                    continue
                all_signals.append(self.make_signal(
                    signal_type="purchase_intent",
                    title=item.get("title", ""),
                    content=item.get("text", "")[:500] if item.get("text") else "",
                    url=f"https://news.ycombinator.com/item?id={sid}",
                    author=item.get("by", ""),
                    score=item.get("score", 0),
                    score_label="upvotes",
                    posted_at=datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
                    metadata={"hn_id": sid, "comments": item.get("descendants", 0)},
                ))
                self.sleep(self.config.RATE_LIMITS["hackernews"])

        # 3. Show HN (product launches)
        r3 = requests.get(f"{self.BASE}/showstories.json", timeout=10)
        if r3.status_code == 200:
            show_ids = r3.json()[:15]
            for sid in show_ids:
                item = self._get_item(sid)
                if not item or not item.get("title"):
                    continue
                all_signals.append(self.make_signal(
                    signal_type="product_listing",
                    title=item.get("title", ""),
                    content=item.get("text", "")[:500] if item.get("text") else "",
                    url=item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                    author=item.get("by", ""),
                    score=item.get("score", 0),
                    score_label="upvotes",
                    posted_at=datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
                    metadata={"hn_id": sid, "comments": item.get("descendants", 0)},
                ))
                self.sleep(self.config.RATE_LIMITS["hackernews"])

        return all_signals
