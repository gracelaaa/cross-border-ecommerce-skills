"""Reddit collector — BrowserAct stealth browser + Google site:reddit.com search.

Reddit blocks all direct/automated access. This collector uses the BrowserAct
stealth browser to search Google for `site:reddit.com <keyword>&tbs=qdr:m`
(past month filter), then extracts post titles, snippets, and metadata from
the Google results page markdown.
"""
import subprocess
import re
import os
import time
from datetime import datetime

from base import BaseCollector
import config


class RedditCollector(BaseCollector):
    name = "reddit"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.ba_bin = cfg.BROWSERACT_BIN
        self.ba_data = os.path.normpath(cfg.BROWSERACT_DATA_DIR)
        self.browser_id = cfg.BROWSERACT_BROWSER_ID

    def _ba_cmd(self, session_name: str, *args) -> str:
        """Run a BrowserAct CLI command and return stdout."""
        cmd = [self.ba_bin] + ["--session", session_name] + list(args)
        env = os.environ.copy()
        env["BROWSERACT_DATA_DIR"] = self.ba_data
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60, env=env
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return ""

    def _search_reddit(self, query: str, session_name: str = "reddit_search") -> list:
        """Search Google for site:reddit.com results and parse them."""
        signals = []
        google_url = (
            f"https://www.google.com/search?q=site:reddit.com+{query.replace(' ', '+').replace('\"', '%22')}"
            f"&num=20&tbs=qdr:m"
        )

        # Open browser session
        self._ba_cmd(session_name, "browser", "open", self.browser_id, google_url)
        time.sleep(2)

        # Get page markdown
        markdown = self._ba_cmd(session_name, "get", "markdown")
        if not markdown:
            self._ba_cmd(session_name, "session", "close")
            return signals

        # Parse Google results: pattern is [### title\n...\nReddit · r/sub\nN+ comments](url)
        # Also handles simpler patterns where title and URL appear separately
        pattern = re.compile(
            r'###\s+(.+?)(?:\n.+?)*?reddit\.com[^\]]*?\]\((https://www\.reddit\.com/r/\S+?)\)',
            re.IGNORECASE | re.DOTALL
        )

        # Alternative: find all reddit URLs and extract associated text
        # Format: ### Title\n  \nReddit · r/subreddit\nN+ comments\n...](url)
        url_pattern = re.compile(
            r'###\s+(.+?)\s*(?:\n.*?)*?(?:Reddit\s*·\s*(r/\w+))?\s*\n.*?(\d+\+?\s*comments)?.*?\]\((https://www\.reddit\.com/r/\S+?)\)',
            re.IGNORECASE | re.DOTALL
        )

        # Simpler approach: find all markdown links to reddit.com
        link_pattern = re.compile(r'\[([^\]]{10,})\]\((https://www\.reddit\.com/r/[^)]+)\)', re.DOTALL)

        for match in link_pattern.finditer(markdown):
            text_block = match.group(1)
            url = match.group(2).split('#')[0].split('?')[0]  # clean URL

            # Extract title from ### header
            title_match = re.search(r'###\s+(.+?)(?:\n|$)', text_block)
            title = title_match.group(1).strip() if title_match else text_block[:100].strip()

            # Extract subreddit
            sub_match = re.search(r'r/(\w+)', url)
            subreddit = f"r/{sub_match.group(1)}" if sub_match else ""

            # Extract comment count
            com_match = re.search(r'(\d+)\+?\s*comments', text_block, re.IGNORECASE)
            comments = int(com_match.group(1)) if com_match else 0

            # Extract snippet (text after title, before Reddit · line)
            snippet_lines = text_block.split('\n')
            snippet = ' '.join(line.strip() for line in snippet_lines if line.strip()
                             and not line.strip().startswith('###')
                             and not line.strip().startswith('Reddit')
                             and 'comments' not in line.lower())[:300]

            signals.append(self._make_reddit_signal(title, snippet, url, query, subreddit, comments))

        # Close session
        self._ba_cmd(session_name, "session", "close")

        return signals

    def _make_reddit_signal(self, title: str, snippet: str, url: str,
                            query: str, subreddit: str, comments: int) -> dict:
        """Create a Reddit signal from Google search result."""
        sig_type = "discussion"
        if "wish there was" in query.lower() or "not satisfied" in query.lower():
            sig_type = "pain_point"
        elif "where can I buy" in query.lower() or "where to find" in query.lower():
            sig_type = "purchase_intent"
        elif "trending" in query.lower() or "best seller" in query.lower():
            sig_type = "trend"
        elif "what should I sell" in query.lower() or "product idea" in query.lower():
            sig_type = "feature_request"

        return self.make_signal(
            signal_type=sig_type,
            title=title,
            content=snippet,
            url=url,
            score=comments,
            score_label="comments",
            keywords=[query, subreddit],
            category=subreddit,
            metadata={
                "subreddit": subreddit,
                "search_query": query,
                "source_detail": "via Google site:reddit.com",
            },
        )

    def collect(self) -> list:
        all_signals = []
        for i, query in enumerate(self.config.REDDIT_QUERIES):
            session = f"reddit_{i}"
            signals = self._search_reddit(query, session)
            all_signals.extend(signals)
            self.sleep(self.config.RATE_LIMITS["reddit"])
        return all_signals
