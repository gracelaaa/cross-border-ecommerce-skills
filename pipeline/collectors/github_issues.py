"""GitHub Issues collector — Search API for feature requests & wishlists."""
import requests

from base import BaseCollector
import config


class GitHubIssuesCollector(BaseCollector):
    name = "github"

    BASE = "https://api.github.com"

    def _search_issues(self, query: str, per_page: int = 15) -> list:
        r = requests.get(
            f"{self.BASE}/search/issues",
            params={
                "q": query,
                "sort": "comments",
                "order": "desc",
                "per_page": per_page,
            },
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=15,
        )
        if r.status_code != 200:
            return []
        return r.json().get("items", [])

    def collect(self) -> list:
        all_signals = []

        for query in self.config.GITHUB_QUERIES:
            items = self._search_issues(query)
            for item in items:
                repo = item.get("repository_url", "").split("repos/")[-1]
                all_signals.append(self.make_signal(
                    signal_type="feature_request",
                    title=item.get("title", ""),
                    content=(item.get("body") or "")[:500] if item.get("body") else "",
                    url=item.get("html_url", ""),
                    author=item.get("user", {}).get("login", ""),
                    score=item.get("comments", 0),
                    score_label="comments",
                    posted_at=item.get("created_at", ""),
                    category=repo,
                    metadata={
                        "repo": repo,
                        "state": item.get("state", ""),
                        "labels": [l.get("name") for l in item.get("labels", [])],
                        "reactions": item.get("reactions", {}).get("total_count", 0),
                    },
                ))
            self.sleep(self.config.RATE_LIMITS["github"])

        # Also search for e-commerce related issues
        for kw in ["amazon fba tool", "dropshipping automation", "ecommerce scraper", "product research"]:
            items = self._search_issues(f"{kw} state:open sort:comments-desc", per_page=5)
            for item in items:
                repo = item.get("repository_url", "").split("repos/")[-1]
                all_signals.append(self.make_signal(
                    signal_type="feature_request",
                    title=item.get("title", ""),
                    content=(item.get("body") or "")[:500] if item.get("body") else "",
                    url=item.get("html_url", ""),
                    author=item.get("user", {}).get("login", ""),
                    score=item.get("comments", 0),
                    score_label="comments",
                    posted_at=item.get("created_at", ""),
                    category=repo,
                    metadata={
                        "repo": repo,
                        "search_keyword": kw,
                        "labels": [l.get("name") for l in item.get("labels", [])],
                    },
                ))
            self.sleep(self.config.RATE_LIMITS["github"])

        return all_signals
