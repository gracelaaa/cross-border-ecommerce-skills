"""
Base collector — common interface for all data source collectors.
"""
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime


class BaseCollector(ABC):
    """Base class for all data source collectors.

    Subclasses must implement collect() which returns a list of signal dicts.
    Each signal dict should have keys:
        source, signal_type, title, content, url, author,
        score, score_label, posted_at, keywords, category, geo, metadata
    """

    name: str = "base"

    def __init__(self, config):
        self.config = config
        self.signals = []
        self.errors = []

    @abstractmethod
    def collect(self) -> list:
        """Collect signals. Returns list of signal dicts."""
        pass

    def sleep(self, seconds: float):
        """Polite delay with jitter."""
        time.sleep(seconds + random.uniform(0, 0.5))

    def make_signal(self, **kwargs) -> dict:
        """Create a signal dict with defaults."""
        sig = {
            "source": self.name,
            "signal_type": "discussion",
            "title": "",
            "content": "",
            "url": "",
            "author": "",
            "score": 0,
            "score_label": "",
            "posted_at": None,          # None = unknown — don't fake timestamps
            "keywords": [],
            "category": "",
            "geo": "US",
            "metadata": {},
        }
        sig.update(kwargs)
        return sig

    def run(self) -> tuple:
        """Execute collection and return (signals, errors)."""
        try:
            signals = self.collect()
            return signals, []
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            return [], [err]
