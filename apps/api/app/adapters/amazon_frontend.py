from urllib.parse import quote_plus

from app.adapters.base import SourceAdapter
from app.core.config import get_settings


class AmazonFrontendAdapter(SourceAdapter):
    name = "amazon_us_frontend"

    async def search(self, keyword: str, category: str | None = None) -> dict:
        settings = get_settings()
        provider = settings.amazon_data_provider.lower().strip()
        if settings.enable_live_sources and provider == "rainforest" and settings.rainforest_api_key:
            try:
                return await self._search_rainforest(keyword, category)
            except Exception as exc:  # pragma: no cover - external provider boundary
                fallback = self._fallback(keyword, category)
                fallback["evidence"].append(
                    {
                        "source_name": "Rainforest API",
                        "source_url": None,
                        "summary": f"Rainforest 调用失败，已回退到保守占位数据：{exc}",
                        "confidence": "low",
                    }
                )
                return fallback
        return self._fallback(keyword, category)

    async def _search_rainforest(self, keyword: str, category: str | None = None) -> dict:
        import httpx

        settings = get_settings()
        params = {
            "api_key": settings.rainforest_api_key,
            "type": "search",
            "amazon_domain": "amazon.com",
            "search_term": keyword,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(settings.rainforest_base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        results = payload.get("search_results") or payload.get("organic_results") or []
        products = []
        for item in results[: max(2, settings.rainforest_max_results)]:
            product = self._parse_rainforest_item(item, category)
            if product["title"]:
                products.append(product)
            if len(products) >= settings.rainforest_max_results:
                break

        if not products:
            raise ValueError("Rainforest response did not include usable search results")

        source_url = f"https://www.amazon.com/s?k={quote_plus(keyword)}"
        return {
            "products": products,
            "evidence": [
                {
                    "source_name": "Rainforest API",
                    "source_url": source_url,
                    "summary": f"已通过 Rainforest API 获取 Amazon US 搜索竞品 {len(products)} 个。",
                    "confidence": "high",
                }
            ],
        }

    def _parse_rainforest_item(self, item: dict, category: str | None) -> dict:
        price = item.get("price") or {}
        rating = item.get("rating")
        ratings_total = item.get("ratings_total") or item.get("reviews_total")
        asin = item.get("asin")
        link = item.get("link")
        if not link and asin:
            link = f"https://www.amazon.com/dp/{asin}"
        return {
            "asin": asin,
            "title": item.get("title") or "",
            "category": category or item.get("category"),
            "price": self._to_float(price.get("value") if isinstance(price, dict) else price),
            "rating": self._to_float(rating),
            "review_count": self._to_int(ratings_total),
            "best_seller_rank": item.get("bestsellers_rank") or item.get("best_seller_rank"),
            "listing_url": link,
            "bullets": item.get("features") or [],
            "aplus_summary": None,
            "variants": {
                "position": item.get("position"),
                "is_prime": item.get("is_prime"),
                "image": item.get("image"),
            },
            "estimated_monthly_sales": self._estimate_sales(ratings_total, rating),
            "image_url": item.get("image"),
            "lifecycle_stage": self._lifecycle(ratings_total),
            "feature_tags": self._feature_tags(item.get("title") or ""),
            "data_source": "rainforest",
            "confidence": "high",
        }

    def _fallback(self, keyword: str, category: str | None = None) -> dict:
        # Conservative fallback: keeps the platform usable when live providers are disabled.
        clean = keyword.strip().title()
        base_price = 18.99 if "clean" in keyword.lower() else 24.99
        return {
            "products": [
                {
                    "asin": None,
                    "title": f"{clean} competitor set",
                    "category": category or "Home & Kitchen",
                    "price": base_price,
                    "rating": 4.3,
                    "review_count": 640,
                    "best_seller_rank": "待确认",
                    "listing_url": f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}",
                    "bullets": ["价格带样本", "卖点和A+内容需二次核验"],
                    "aplus_summary": "待采集",
                    "variants": {},
                    "confidence": "low",
                }
            ],
            "evidence": [
                {
                    "source_name": "Amazon US Search",
                    "source_url": f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}",
                    "summary": "搜索结果入口已记录；前台详情需要合规采集或人工复核。",
                    "confidence": "low",
                }
            ],
        }

    def _to_float(self, value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(str(value).replace(",", "").replace("$", ""))
        except ValueError:
            return None

    def _to_int(self, value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(float(str(value).replace(",", "")))
        except ValueError:
            return None

    def _estimate_sales(self, review_count: object, rating: object) -> float | None:
        reviews = self._to_int(review_count)
        if reviews is None:
            return None
        rating_value = self._to_float(rating) or 4.0
        velocity = 0.22 if rating_value >= 4.5 else 0.16
        return round(max(20, min(5000, reviews * velocity)), 0)

    def _lifecycle(self, review_count: object) -> str:
        reviews = self._to_int(review_count) or 0
        if reviews >= 3000:
            return "成熟期"
        if reviews >= 500:
            return "增长期"
        return "验证期"

    def _feature_tags(self, title: str) -> list[str]:
        lowered = title.lower()
        tags = []
        for token, label in [
            ("set", "套装"),
            ("pack", "多件装"),
            ("portable", "便携"),
            ("organizer", "收纳"),
            ("clean", "清洁"),
            ("waterproof", "防水"),
            ("reusable", "可复用"),
        ]:
            if token in lowered:
                tags.append(label)
        return tags[:5]
