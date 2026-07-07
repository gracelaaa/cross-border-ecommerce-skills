"""Amazon collector — fetchlib (curl_cffi) for product search + reviews.

Uses fetchlib with curl_cffi TLS impersonation. Falls back to Jina markdown
if curl_cffi gets blocked. Parses both HTML (L1) and markdown (L2) formats.
"""
import sys
import os
import re
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
from fetchlib.fetchlib import Fetcher

from base import BaseCollector
import config


class AmazonCollector(BaseCollector):
    name = "amazon"

    def __init__(self, cfg):
        super().__init__(cfg)
        # Amazon blocks curl_cffi with bm-verify redirect; use Jina directly
        self.fetcher = Fetcher(tiers=("jina",), respect_robots=False, pace=True)
        self.base_url = "https://www.amazon.com"

    def _parse_html_products(self, html: str, keyword: str) -> list:
        """Parse Amazon search results from HTML (curl_cffi tier)."""
        signals = []
        soup = BeautifulSoup(html, "html.parser")

        # Try multiple selectors for product cards
        items = soup.select('[data-component-type="s-search-result"]')
        if not items:
            items = soup.select('[data-asin]:not([data-asin=""])')

        for item in items[:15]:
            # Title: try multiple selectors
            title_el = (item.select_one("h2 a span") or
                       item.select_one("h2 span") or
                       item.select_one(".s-line-clamp-1 span"))
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue

            # ASIN
            asin = item.get("data-asin", "")
            if not asin:
                link_el = item.select_one("h2 a")
                if link_el and "/dp/" in link_el.get("href", ""):
                    asin = link_el["href"].split("/dp/")[1].split("/")[0]

            # Price
            price_el = item.select_one(".a-price .a-offscreen") or item.select_one(".a-color-price")
            price = price_el.get_text(strip=True) if price_el else ""

            # Rating
            rating_el = item.select_one('i.a-icon-star-small span') or item.select_one('.a-icon-alt')
            rating_str = rating_el.get_text(strip=True) if rating_el else "0"
            rating = float(rating_str.split(" ")[0]) if rating_str and rating_str[0].isdigit() else 0

            # Review count
            review_count = 0
            review_el = item.select_one('[class*="review-count"]') or item.select_one("span.a-size-base.s-underline-text")
            if review_el:
                txt = review_el.get_text(strip=True).replace(",", "")
                nums = re.findall(r"\d+", txt)
                review_count = int(nums[0]) if nums else 0

            signals.append(self.make_signal(
                signal_type="product_listing",
                title=title,
                content=f"Price: {price} | Rating: {rating} | Reviews: {review_count}",
                url=f"{self.base_url}/dp/{asin}" if asin else "",
                score=review_count,
                score_label="review_count",
                category=keyword,
                metadata={"asin": asin, "price": price, "rating": rating},
            ))

        return signals

    def _parse_markdown_products(self, markdown: str, keyword: str) -> list:
        """Parse Amazon search results from Jina markdown (L2 tier)."""
        signals = []
        lines = markdown.split("\n")

        for line in lines:
            line = line.strip()
            # Jina markdown often formats product titles as headers or links
            if line.startswith("###") and len(line) > 10:
                title = line.lstrip("#").strip()
                if title and not title.startswith("Amazon") and not title.startswith("Sponsored"):
                    signals.append(self.make_signal(
                        signal_type="product_listing",
                        title=title,
                        content="",
                        url="",
                        category=keyword,
                        metadata={"source_tier": "jina"},
                    ))
            elif line.startswith("[") and "amazon.com" in line.lower() and "](" in line:
                match = re.match(r"\[([^\]]{10,})\]\(([^)]+)\)", line)
                if match:
                    title, url = match.group(1), match.group(2)
                    if not title.lower().startswith(("amazon", "sponsored", "see more")):
                        signals.append(self.make_signal(
                            signal_type="product_listing",
                            title=title,
                            content="",
                            url=url,
                            category=keyword,
                            metadata={"source_tier": "jina"},
                        ))

        return signals

    def _search_products(self, keyword: str) -> list:
        """Search Amazon for products."""
        url = f"{self.base_url}/s?k={keyword.replace(' ', '+')}"
        result = self.fetcher.fetch(url)

        if not result.get("text"):
            return []

        tier = result.get("tier", "")
        text = result["text"]

        if tier == "curl_cffi":
            # HTML parsing
            signals = self._parse_html_products(text, keyword)
            if signals:
                return signals
            # If HTML parsing fails, try markdown parsing as fallback
            return self._parse_markdown_products(text, keyword)
        else:
            # Jina markdown
            return self._parse_markdown_products(text, keyword)

    def _fetch_reviews(self, asin: str) -> list:
        """Fetch top reviews for a product."""
        signals = []
        url = f"{self.base_url}/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?reviewerType=all_reviews"
        result = self.fetcher.fetch(url)
        if not result.get("text"):
            return signals

        soup = BeautifulSoup(result["text"], "html.parser")
        reviews = soup.select('[data-hook="review"]')

        for review in reviews[:10]:
            title_el = review.select_one('[data-hook="review-title"] span') or review.select_one('[data-hook="review-title"]')
            title = title_el.get_text(strip=True) if title_el else ""
            body_el = review.select_one('[data-hook="review-body"] span') or review.select_one('[data-hook="review-body"]')
            body = body_el.get_text(strip=True)[:500] if body_el else ""
            rating_el = review.select_one('[data-hook="review-star-rating"] span') or review.select_one('.a-icon-alt')
            rating_str = rating_el.get_text(strip=True) if rating_el else "0"
            rating = float(rating_str.split(" ")[0]) if rating_str and rating_str[0].isdigit() else 0
            author_el = review.select_one(".a-profile-name")
            author = author_el.get_text(strip=True) if author_el else ""
            date_el = review.select_one('[data-hook="review-date"]')
            date_str = date_el.get_text(strip=True) if date_el else ""

            signals.append(self.make_signal(
                signal_type="review",
                title=title,
                content=body,
                url=f"{self.base_url}/dp/{asin}",
                author=author,
                score=rating,
                score_label="rating",
                posted_at=date_str,
                category=asin,
                metadata={"asin": asin, "rating": rating},
            ))

        return signals

    def collect(self) -> list:
        all_signals = []
        for keyword in self.config.AMAZON_SEARCH_KEYWORDS:
            products = self._search_products(keyword)
            all_signals.extend(products)
            for p in products[:2]:
                asin = p.get("metadata", {}).get("asin", "")
                if asin:
                    reviews = self._fetch_reviews(asin)
                    all_signals.extend(reviews)
                    self.sleep(self.config.RATE_LIMITS["amazon"])
            self.sleep(self.config.RATE_LIMITS["amazon"])
        return all_signals
