"""Product Hunt collector — fetchlib (Jina) for trending products."""
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
from fetchlib.fetchlib import Fetcher

from base import BaseCollector
import config


class ProductHuntCollector(BaseCollector):
    name = "producthunt"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.fetcher = Fetcher(tiers=("curl_cffi", "jina"), respect_robots=False, pace=True)

    def _parse_products(self, markdown: str) -> list:
        """Parse Product Hunt page for product listings."""
        signals = []
        lines = markdown.split("\n")

        for line in lines:
            line = line.strip()
            # Product Hunt products appear as links with descriptions
            if line.startswith("[") and "](" in line and "producthunt.com" in line.lower():
                match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", line)
                if match:
                    title, url = match.group(1), match.group(2)
                    signals.append(self.make_signal(
                        signal_type="product_listing",
                        title=title,
                        content="",
                        url=url,
                        signal_type_v2="trending_product",
                        metadata={"platform": "producthunt"},
                    ))
            elif line.startswith("###") and len(line) > 5:
                title = line.lstrip("#").strip()
                signals.append(self.make_signal(
                    signal_type="trend",
                    title=title,
                    content="",
                    url="https://www.producthunt.com",
                    metadata={"platform": "producthunt"},
                ))

        return signals

    def collect(self) -> list:
        all_signals = []
        # Today's products
        url = "https://www.producthunt.com/"
        result = self.fetcher.fetch(url)
        if result.get("text"):
            products = self._parse_products(result["text"])
            all_signals.extend(products)

        self.sleep(self.config.RATE_LIMITS["producthunt"])

        # Also fetch a category page
        url = "https://www.producthunt.com/topics/e-commerce"
        result = self.fetcher.fetch(url)
        if result.get("text"):
            products = self._parse_products(result["text"])
            all_signals.extend(products)

        return all_signals
