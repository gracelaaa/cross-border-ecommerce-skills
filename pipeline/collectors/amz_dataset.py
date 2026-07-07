"""Amazon public dataset collector — HuggingFace McAuley-Lab/Amazon-Reviews-2023.

Downloads JSONL review files for specified categories and samples reviews
for demand signal extraction (pain points, positive/negative feedback).
"""
import os
import json
import random
from huggingface_hub import hf_hub_download

from base import BaseCollector
import config


class AmazonDatasetCollector(BaseCollector):
    name = "amz_dataset"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.repo_id = "McAuley-Lab/Amazon-Reviews-2023"
        self.cache_dir = os.path.join(cfg.PIPELINE_DIR, "data", "amz_dataset")

    def _download_reviews(self, category: str) -> str:
        """Download review JSONL for a category from HuggingFace."""
        filename = f"raw/review_categories/{category}.jsonl"
        os.makedirs(self.cache_dir, exist_ok=True)
        local_path = hf_hub_download(
            self.repo_id,
            filename,
            repo_type="dataset",
            cache_dir=self.cache_dir,
        )
        return local_path

    def _classify_review(self, rating: int, title: str, text: str) -> str:
        """Classify a review into a signal type."""
        if rating <= 2:
            return "pain_point"
        elif rating >= 4:
            # Check if review mentions missing features
            t = (title + text).lower()
            if any(w in t for w in ["wish", "missing", "should have", "if only", "needs"]):
                return "pain_point"
            return "review"
        return "review"

    def _extract_keywords(self, title: str, text: str) -> list:
        """Simple keyword extraction from review text."""
        combined = (title + " " + text).lower()
        # Common e-commerce keywords
        keywords = []
        markers = [
            "quality", "price", "shipping", "delivery", " packaging", "size",
            "color", "material", "design", "durable", "broken", "defective",
            "refund", "return", "fast", "slow", "expensive", "cheap", "value",
            "recommend", "love", "hate", "disappointed", "satisfied", "perfect",
        ]
        for m in markers:
            if m.strip() in combined:
                keywords.append(m.strip())
        return keywords[:5]

    def _process_reviews(self, file_path: str, category: str, sample_size: int) -> list:
        """Read JSONL and sample reviews."""
        signals = []
        reviews = []

        # Read all reviews (JSONL format, one JSON object per line)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    review = json.loads(line.strip())
                    reviews.append(review)
                except json.JSONDecodeError:
                    continue
                # Stop after enough reviews for sampling
                if len(reviews) >= sample_size * 3:
                    break

        # Sample a subset for processing
        sample = random.sample(reviews, min(sample_size, len(reviews)))

        for review in sample:
            rating = review.get("rating", 0)
            title = review.get("title", "")
            text = review.get("text", "")
            asin = review.get("asin", "")
            user_id = review.get("user_id", "")
            verified = review.get("verified_purchase", False)
            helpful_votes = review.get("helpful_votes", 0)
            timestamp = review.get("timestamp", "")

            if not title and not text:
                continue

            signals.append(self.make_signal(
                signal_type=self._classify_review(rating, title, text),
                title=title[:200],
                content=text[:500],
                url=f"https://www.amazon.com/dp/{asin}" if asin else "",
                author=user_id,
                score=rating,
                score_label="rating",
                posted_at=str(timestamp) if timestamp else "",
                keywords=self._extract_keywords(title, text),
                category=category,
                metadata={
                    "asin": asin,
                    "rating": rating,
                    "verified_purchase": verified,
                    "helpful_votes": helpful_votes,
                    "dataset": "McAuley-Lab/Amazon-Reviews-2023",
                },
            ))

        return signals

    def collect(self) -> list:
        all_signals = []
        for category in self.config.AMZ_DATASET_CATEGORIES:
            try:
                file_path = self._download_reviews(category)
                signals = self._process_reviews(
                    file_path, category, self.config.AMZ_DATASET_SAMPLE_SIZE
                )
                all_signals.extend(signals)
            except Exception as e:
                self.errors.append(f"Failed to download {category}: {e}")
        return all_signals
