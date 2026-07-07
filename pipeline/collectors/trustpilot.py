"""Trustpilot collector — fetchlib (Jina) for company reviews."""
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
from fetchlib.fetchlib import Fetcher

from base import BaseCollector
import config


class TrustpilotCollector(BaseCollector):
    name = "trustpilot"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.fetcher = Fetcher(tiers=("curl_cffi", "jina"), respect_robots=False, pace=True)

    def _parse_reviews(self, markdown: str, company: str) -> list:
        """Parse Jina markdown output for Trustpilot reviews."""
        signals = []
        lines = markdown.split("\n")
        current_review = {}
        in_review = False

        for line in lines:
            line = line.strip()
            # Jina returns markdown headers for review titles
            if line.startswith("###") and len(line) > 5:
                if current_review:
                    signals.append(self.make_signal(
                        signal_type="review",
                        title=current_review.get("title", ""),
                        content=current_review.get("body", ""),
                        url=f"https://www.trustpilot.com/review/{company}",
                        author=current_review.get("author", ""),
                        score=current_review.get("rating", 0),
                        score_label="rating",
                        category=company,
                        metadata={"company": company, "rating": current_review.get("rating", 0)},
                    ))
                current_review = {"title": line.lstrip("#").strip()}
                in_review = True
            elif in_review and "star" in line.lower():
                nums = re.findall(r"(\d+)", line)
                if nums:
                    current_review["rating"] = int(nums[0])
            elif in_review and line.startswith("Date of experience:"):
                current_review["posted_at"] = line.replace("Date of experience:", "").strip()
            elif in_review and len(line) > 20 and not line.startswith("|") and not line.startswith("---"):
                if "body" not in current_review:
                    current_review["body"] = line
                else:
                    current_review["body"] += " " + line

        # Don't forget the last review
        if current_review and current_review.get("title"):
            signals.append(self.make_signal(
                signal_type="review",
                title=current_review.get("title", ""),
                content=current_review.get("body", ""),
                url=f"https://www.trustpilot.com/review/{company}",
                author=current_review.get("author", ""),
                score=current_review.get("rating", 0),
                score_label="rating",
                category=company,
                metadata={"company": company},
            ))

        return signals

    def collect(self) -> list:
        all_signals = []
        for company in self.config.TRUSTPILOT_CATEGORIES:
            url = f"https://www.trustpilot.com/review/{company}"
            result = self.fetcher.fetch(url)
            if result.get("text"):
                reviews = self._parse_reviews(result["text"], company)
                all_signals.extend(reviews)
            self.sleep(self.config.RATE_LIMITS["trustpilot"])
        return all_signals
