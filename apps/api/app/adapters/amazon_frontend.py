from app.adapters.base import SourceAdapter


class AmazonFrontendAdapter(SourceAdapter):
    name = "amazon_us_frontend"

    async def search(self, keyword: str, category: str | None = None) -> dict:
        # Production hook: replace this conservative stub with approved scraping API,
        # PA-API, or a compliant data provider. Until verified, confidence remains low.
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
