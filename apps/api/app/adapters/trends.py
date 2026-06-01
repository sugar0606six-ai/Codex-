from app.adapters.base import SourceAdapter


class PublicTrendAdapter(SourceAdapter):
    name = "public_trends"

    async def search(self, keyword: str, category: str | None = None) -> dict:
        seed = sum(ord(ch) for ch in keyword) % 28
        score = min(92, 52 + seed)
        direction = "rising" if score >= 65 else "stable"
        query = keyword.replace(" ", "%20")
        return {
            "snapshots": [
                {
                    "source": "Google Trends",
                    "window_days": 30,
                    "trend_score": score,
                    "direction": direction,
                    "evidence_url": f"https://trends.google.com/trends/explore?geo=US&q={query}",
                    "summary": "趋势入口已记录；未启用实时采集时标记为低置信度。",
                    "confidence": "low",
                },
                {
                    "source": "Reddit / TikTok / Blogs",
                    "window_days": 60,
                    "trend_score": max(40, score - 8),
                    "direction": direction,
                    "evidence_url": None,
                    "summary": "站外讨论热度需要接入 Firecrawl、TikTok Creative Center 或 Reddit API 验证。",
                    "confidence": "low",
                },
            ]
        }
