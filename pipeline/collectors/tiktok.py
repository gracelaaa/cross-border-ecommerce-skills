"""TikTok collector — oEmbed metadata + curl_cffi page scraping."""
import re
import json
from curl_cffi import requests as cffi_requests

from base import BaseCollector
import config


class TikTokCollector(BaseCollector):
    name = "tiktok"

    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    def _search_videos(self, session, query: str, max_results: int = 10) -> list:
        """Search TikTok and parse results."""
        signals = []
        url = f"https://www.tiktok.com/search?q={query.replace(' ', '+')}"
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            return signals

        # TikTok embeds data in SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
        for pattern_name, pattern in [
            ("SIGI_STATE", r"SIGI_STATE\s*=\s*(\{.*?\});"),
            ("UNIVERSAL", r'"__UNIVERSAL_DATA_FOR_REHYDRATION__"\s*:\s*(\{.*?\})\s*</script>'),
            ("SIGI_STATE_NEW", r'<script id="SIGI_STATE"[^>]*>(\{.*?\})</script>'),
        ]:
            match = re.search(pattern, r.text)
            if match:
                try:
                    data = json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

                # Navigate to search results
                items = (data.get("ItemModule", {}) or
                         data.get("webapp", {}).get("video", {}).get("itemList", []) or
                         [])

                count = 0
                for vid_id, v in (items.items() if isinstance(items, dict) else enumerate(items)):
                    v = v if isinstance(v, dict) else {}
                    desc = v.get("desc", "")
                    author = v.get("author", "").split(" ")[0] if isinstance(v.get("author"), str) else \
                             v.get("author", {}).get("uniqueId", "") if isinstance(v.get("author"), dict) else ""
                    stats = v.get("stats", {}) if isinstance(v.get("stats"), dict) else {}
                    plays = stats.get("playCount", 0)
                    likes = stats.get("diggCount", 0)
                    comments = stats.get("commentCount", 0)
                    create_time = v.get("createTime", "")

                    if not desc:
                        continue

                    signals.append(self.make_signal(
                        signal_type="video_content",
                        title=desc[:100],
                        content=desc[:300],
                        url=f"https://www.tiktok.com/@{author}/video/{vid_id}" if vid_id else "",
                        author=author,
                        score=plays,
                        score_label="views",
                        posted_at=str(create_time) if create_time else "",
                        keywords=[query],
                        metadata={
                            "likes": likes,
                            "comments_count": comments,
                            "plays": plays,
                        },
                    ))
                    count += 1
                    if count >= max_results:
                        break
                break

        return signals

    def collect(self) -> list:
        all_signals = []
        session = cffi_requests.Session(impersonate="chrome131")

        search_queries = [
            "amazon finds 2025",
            "trending products tiktok",
            "tiktok made me buy it",
            "viral products",
        ]

        for q in search_queries:
            videos = self._search_videos(session, q, max_results=8)
            all_signals.extend(videos)
            self.sleep(self.config.RATE_LIMITS["tiktok"])

        return all_signals
