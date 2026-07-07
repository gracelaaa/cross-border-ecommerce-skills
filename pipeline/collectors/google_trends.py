"""Google Trends collector — curl_cffi session + explore API."""
import json
from curl_cffi import requests as cffi_requests

from base import BaseCollector
import config


class GoogleTrendsCollector(BaseCollector):
    name = "google_trends"

    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    def _strip_prefix(self, text: str) -> str:
        """Google Trends API prepends )]}' and sometimes a comma to JSON responses."""
        for prefix in [")]}'", ")]}"]:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        # Strip leading commas, newlines, whitespace (Google Trends quirks)
        return text.lstrip(",\n\r\t ")

    def _safe_json(self, text: str):
        """Parse JSON with prefix stripping and error handling."""
        try:
            return json.loads(self._strip_prefix(text))
        except (json.JSONDecodeError, TypeError):
            return None

    def _explore_keyword(self, session, keyword: str) -> list:
        """Get interest over time + related queries for a keyword."""
        signals = []
        explore_req = json.dumps({
            "comparisonItem": [{"keyword": keyword, "geo": "US", "time": "today 3-m"}],
            "category": 0,
            "property": "",
        })

        r = session.get(
            "https://trends.google.com/trends/api/explore",
            params={"hl": "en-US", "tz": 240, "req": explore_req},
            headers={"Accept": "application/json", "User-Agent": self.UA},
            timeout=15,
        )
        if r.status_code != 200:
            return signals

        data = self._safe_json(r.text)
        if not data:
            return signals
        widgets = data.get("widgets", [])

        for w in widgets:
            wtype = w.get("type", "")
            token = w.get("token")
            req_data = json.dumps(w.get("request", {}))

            # Widget types: fe_line_chart (timeseries), fe_related_searches (related queries/topics)
            if wtype in ("TIMESERIES", "fe_line_chart") and token:
                r2 = session.get(
                    "https://trends.google.com/trends/api/widgetdata/multiline",
                    params={"hl": "en-US", "tz": 240, "token": token, "req": req_data},
                    headers={"Accept": "application/json", "User-Agent": self.UA},
                    timeout=15,
                )
                if r2.status_code == 200 and r2.text:
                    ts_data = self._safe_json(r2.text)
                    if ts_data:
                        lines = ts_data.get("default", {}).get("timelineData", [])
                        if lines:
                            last = lines[-1]
                            first = lines[0]
                            vals = [l.get("value", [0])[0] if isinstance(l.get("value"), list) else l.get("value", 0) for l in lines]
                            avg_val = sum(vals) / max(len(vals), 1)
                            signals.append(self.make_signal(
                                signal_type="trend",
                                title=f"Google Trends: {keyword}",
                                content=f"Interest over time (3 months): {len(lines)} data points. "
                                       f"Start: {first.get('formattedTime')} value={first.get('value')}. "
                                       f"End: {last.get('formattedTime')} value={last.get('value')}. "
                                       f"Average: {avg_val:.1f}",
                                url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}&geo=US",
                                score=vals[-1] if vals else 0,
                                score_label="search_volume",
                                keywords=[keyword],
                                geo="US",
                                metadata={
                                    "keyword": keyword,
                                    "data_points": len(lines),
                                    "first_value": first.get("value"),
                                    "last_value": last.get("value"),
                                    "timeframe": "today 3-m",
                                },
                            ))

            elif wtype in ("RELATED_QUERIES", "fe_related_searches") and token:
                r3 = session.get(
                    "https://trends.google.com/trends/api/widgetdata/relatedsearches",
                    params={"hl": "en-US", "tz": 240, "token": token, "req": req_data},
                    headers={"Accept": "application/json", "User-Agent": self.UA},
                    timeout=15,
                )
                if r3.status_code == 200 and r3.text:
                    rq_data = self._safe_json(r3.text)
                    if rq_data:
                        ranked_lists = rq_data.get("default", {}).get("rankedList", [])
                        for rl in ranked_lists:
                            for item in (rl.get("rankedKeyword") or [])[:10]:
                                query = item.get("query", "")
                                val = item.get("value", 0)
                                signals.append(self.make_signal(
                                    signal_type="trend",
                                    title=f"Related query: {query}",
                                    content=f"Related to '{keyword}' with trend value {val}",
                                    url=f"https://trends.google.com/trends/explore?q={query.replace(' ', '+')}&geo=US",
                                    score=val,
                                    score_label="trend_value",
                                    keywords=[keyword, query],
                                    geo="US",
                                    metadata={
                                        "parent_keyword": keyword,
                                        "related_query": query,
                                    },
                                ))

            self.sleep(0.5)

        return signals

    def collect(self) -> list:
        all_signals = []
        session = cffi_requests.Session(impersonate="chrome131")
        # Warm up session with cookies (ignore 429 on warmup)
        try:
            session.get("https://trends.google.com/trends/explore", timeout=10,
                        headers={"User-Agent": self.UA})
        except Exception:
            pass

        for kw in self.config.TRENDS_KEYWORDS:
            signals = self._explore_keyword(session, kw)
            all_signals.extend(signals)
            self.sleep(self.config.RATE_LIMITS["google_trends"])

        return all_signals
