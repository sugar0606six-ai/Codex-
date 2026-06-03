from sqlalchemy.orm import Session
from app.adapters.amazon_frontend import AmazonFrontendAdapter
from app.adapters.trends import PublicTrendAdapter
from app.adapters.westmonth_skill import WestMonthSkillAdapter
from app.models.entities import (
    AmazonProduct,
    CompetitorLink,
    Opportunity,
    ProfitCalculation,
    RiskAssessment,
    SearchKeyword,
    SourceEvidence,
    TrendSnapshot,
)
from app.services.scoring import ScoreInput, decision, margin_score_from_rate, opportunity_score, risk_level


RISKY_TERMS = {"disney", "tesla", "stanley", "iphone", "medical", "pesticide", "kids", "heated", "battery"}


class OpportunityAnalyzer:
    def __init__(self) -> None:
        self.amazon = AmazonFrontendAdapter()
        self.trends = PublicTrendAdapter()
        self.catalog = WestMonthSkillAdapter()

    async def analyze_keyword(self, db: Session, keyword: str, category: str | None, user_id: int | None) -> Opportunity:
        kw = SearchKeyword(keyword=keyword.strip(), category=category, status="running", requested_by=user_id)
        db.add(kw)
        db.flush()

        amazon_data = await self.amazon.search(keyword, category)
        trend_data = await self.trends.search(keyword, category)
        catalog_data = self.catalog.match(keyword)

        amazon_products = [self._store_amazon(db, product) for product in amazon_data["products"][:5]]
        primary_product = amazon_products[0]
        for product in amazon_products:
            db.add(
                CompetitorLink(
                    keyword_id=kw.id,
                    amazon_product_id=product.id,
                    url=product.listing_url or "https://www.amazon.com",
                    title=product.title,
                    price=product.price,
                    rating=product.rating,
                    review_count=product.review_count,
                    asin=product.asin,
                    estimated_monthly_sales=product.estimated_monthly_sales,
                    image_url=product.image_url,
                    differentiation=self._competitor_gap(product),
                )
            )
        for item in trend_data["snapshots"]:
            db.add(TrendSnapshot(keyword_id=kw.id, **item))
        for evidence in amazon_data["evidence"]:
            db.add(SourceEvidence(entity_type="keyword", entity_id=kw.id, **evidence))

        demand = round(sum(item["trend_score"] for item in trend_data["snapshots"]) / len(trend_data["snapshots"]), 2)
        competition = self._competition_score(amazon_products)
        risk = self._risk_score(keyword)
        selling_price = self._mainstream_price(amazon_products) or primary_product.price or 19.99
        product_cost = round(selling_price * 0.32, 2)
        profit = self._profit(keyword_id=kw.id, selling_price=selling_price, product_cost=product_cost)
        margin_score = margin_score_from_rate(profit.margin_rate)
        catalog_score = float(catalog_data.get("catalog_match_score", 45))
        final_score = opportunity_score(
            ScoreInput(
                demand=demand,
                margin=margin_score,
                competition=competition,
                catalog_match=catalog_score,
                risk=risk,
            )
        )
        action = decision(final_score, risk, profit.margin_rate)

        db.add(profit)
        db.add(
            RiskAssessment(
                keyword_id=kw.id,
                infringement_risk="high" if risk >= 70 else "medium" if risk >= 40 else "low",
                patent_risk="待确认" if risk >= 40 else "low",
                trademark_risk="待确认" if any(term in keyword.lower() for term in RISKY_TERMS) else "low",
                compliance_risk="medium" if any(term in keyword.lower() for term in ["chemical", "pesticide", "battery"]) else "low",
                risk_score=risk,
                review_required=risk >= 40,
                rationale="关键词命中品牌、合规或功能风险时默认要求人工复核；本结果不是法律意见。",
            )
        )

        opportunity = Opportunity(
            keyword_id=kw.id,
            catalog_product_id=None,
            title=keyword.strip().title(),
            category=category or primary_product.category,
            target_audience=self._audience(keyword),
            lifecycle_stage=primary_product.lifecycle_stage or ("增长期" if demand >= 65 else "验证期"),
            seasonality="Q4/Prime Day 需复核" if "car" not in keyword.lower() else "全年，冬夏车品有波峰",
            top_features=self._top_features(amazon_products),
            differentiation="结合 WestMonth 现货 SKU 做颜色、套装、配件或包装差异化。",
            demand_score=demand,
            margin_score=margin_score,
            competition_score=competition,
            catalog_match_score=catalog_score,
            risk_score=risk,
            opportunity_score=final_score,
            listing_difficulty="高" if competition < 45 or risk >= 70 else "中" if competition < 70 else "低",
            risk_level=risk_level(risk),
            recommended_action=action,
            confidence="medium" if catalog_data.get("confidence") == "medium" else "low",
        )
        db.add(opportunity)
        kw.status = "completed"
        db.commit()
        db.refresh(opportunity)
        return opportunity

    def _store_amazon(self, db: Session, payload: dict) -> AmazonProduct:
        product = AmazonProduct(**payload)
        db.add(product)
        db.flush()
        return product

    def _competition_score(self, products: list[AmazonProduct]) -> float:
        reviews = sum((product.review_count or 0) for product in products) / max(1, len(products))
        rating = sum((product.rating or 0) for product in products if product.rating) / max(
            1, len([product for product in products if product.rating])
        )
        base = 82
        if reviews > 3000:
            base -= 34
        elif reviews > 1000:
            base -= 22
        elif reviews > 300:
            base -= 12
        if rating and rating >= 4.6:
            base -= 8
        return max(20, min(95, base))

    def _mainstream_price(self, products: list[AmazonProduct]) -> float | None:
        prices = sorted(product.price for product in products if product.price and product.price > 0)
        if not prices:
            return None
        middle = len(prices) // 2
        if len(prices) % 2:
            return round(prices[middle], 2)
        return round((prices[middle - 1] + prices[middle]) / 2, 2)

    def _competitor_gap(self, product: AmazonProduct) -> str:
        tags = product.feature_tags or []
        if "套装" in tags or "多件装" in tags:
            return "竞品强调套装/多件装，WestMonth 可从组合数量、配件和包装说明差异化。"
        if product.review_count and product.review_count > 1000:
            return "竞品评论量高，需避开同质化卖点，优先寻找轻量改款或细分场景。"
        return "竞品仍有验证空间，可重点比较价格带、评分和功能标签。"

    def _top_features(self, products: list[AmazonProduct]) -> list[str]:
        tags: list[str] = []
        for product in products:
            tags.extend(product.feature_tags or [])
        unique = []
        for tag in tags + ["可套装化", "轻小件优先", "差异化包装和说明书"]:
            if tag not in unique:
                unique.append(tag)
        return unique[:6]

    def _risk_score(self, keyword: str) -> float:
        lowered = keyword.lower()
        score = 22
        if any(term in lowered for term in RISKY_TERMS):
            score += 45
        if any(term in lowered for term in ["chemical", "spray", "battery", "heated", "child"]):
            score += 18
        return min(95, score)

    def _profit(self, keyword_id: int, selling_price: float, product_cost: float) -> ProfitCalculation:
        referral_fee = round(selling_price * 0.15, 2)
        fba_fee = 4.2
        inbound_shipping = 1.1
        ppc_buffer = round(selling_price * 0.08, 2)
        net = round(selling_price - product_cost - referral_fee - fba_fee - inbound_shipping - ppc_buffer, 2)
        rate = round(net / selling_price, 4)
        return ProfitCalculation(
            keyword_id=keyword_id,
            selling_price=selling_price,
            product_cost=product_cost,
            referral_fee=referral_fee,
            fba_fee=fba_fee,
            inbound_shipping=inbound_shipping,
            ppc_buffer=ppc_buffer,
            net_margin=net,
            margin_rate=rate,
            confidence="estimated",
        )

    def _audience(self, keyword: str) -> str:
        if "car" in keyword.lower() or "auto" in keyword.lower():
            return "美国有车家庭、通勤用户、车内收纳和清洁需求人群。"
        return "美国中产家庭、租房用户、宠物家庭、注重效率的家居清洁消费者。"
