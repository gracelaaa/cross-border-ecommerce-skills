"""YouTube collector — oEmbed metadata + curl_cffi page scraping for search results."""
import re
import json
from curl_cffi import requests as cffi_requests

from base import BaseCollector
import config


class YouTubeCollector(BaseCollector):
    name = "youtube"

    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    def _search_videos(self, session, query: str, max_results: int = 10) -> list:
        """Search YouTube and parse video results from page HTML."""
        signals = []
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            return signals

        # Extract ytInitialData from page
        match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", r.text)
        if not match:
            return signals

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return signals

        # Navigate the JSON to find video results
        contents = (data.get("contents", {})
                        .get("twoColumnSearchResultsRenderer", {})
                        .get("primaryContents", {})
                        .get("sectionListRenderer", {})
                        .get("contents", []))

        count = 0
        for section in contents:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                v = item.get("videoRenderer", {})
                if not v:
                    continue

                vid_id = v.get("videoId", "")
                title = v.get("title", {}).get("runs", [{}])[0].get("text", "")
                channel = v.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                views_str = v.get("viewCountText", {}).get("simpleText", "0")
                views = int(re.sub(r"[^\d]", "", views_str) or "0")
                desc = v.get("descriptionSnippet", {}).get("runs", [{}])[0].get("text", "")
                published = v.get("publishedTimeText", {}).get("simpleText", "")

                if not title or not vid_id:
                    continue

                signals.append(self.make_signal(
                    signal_type="video_content",
                    title=title,
                    content=desc[:300],
                    url=f"https://www.youtube.com/watch?v={vid_id}",
                    author=channel,
                    score=views,
                    score_label="views",
                    posted_at=published,
                    keywords=[query],
                    metadata={
                        "video_id": vid_id,
                        "views": views,
                        "channel": channel,
                    },
                ))
                count += 1
                if count >= max_results:
                    break
            if count >= max_results:
                break

        return signals

    def collect(self) -> list:
        all_signals = []
        session = cffi_requests.Session(impersonate="chrome131")

        search_queries = [
            "amazon fba product research 2025",
            "best products to sell online 2025",
            "dropshipping winning products",
            "trending products to sell",
        ]

        for q in search_queries:
            videos = self._search_videos(session, q, max_results=10)
            all_signals.extend(videos)
            self.sleep(self.config.RATE_LIMITS["youtube"])

        return all_signals
