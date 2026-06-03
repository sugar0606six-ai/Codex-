from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="analyst")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CatalogProduct(Base, TimestampMixin):
    __tablename__ = "catalog_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500), index=True)
    category: Mapped[str | None] = mapped_column(String(255))
    cost: Mapped[float | None] = mapped_column(Float)
    sale_price: Mapped[float | None] = mapped_column(Float)
    inventory: Mapped[int | None] = mapped_column(Integer)
    weight: Mapped[str | None] = mapped_column(String(120))
    dimensions: Mapped[str | None] = mapped_column(String(120))
    variants: Mapped[dict | None] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(Text)
    images: Mapped[list | None] = mapped_column(JSON)
    supplier: Mapped[str | None] = mapped_column(String(255), default="WestMonth")
    source_url: Mapped[str | None] = mapped_column(String(1000))


class SearchKeyword(Base, TimestampMixin):
    __tablename__ = "search_keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="queued")
    requested_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class AmazonProduct(Base, TimestampMixin):
    __tablename__ = "amazon_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    asin: Mapped[str | None] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(700))
    category: Mapped[str | None] = mapped_column(String(255))
    price: Mapped[float | None] = mapped_column(Float)
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None] = mapped_column(Integer)
    best_seller_rank: Mapped[str | None] = mapped_column(String(255))
    listing_url: Mapped[str | None] = mapped_column(String(1000))
    bullets: Mapped[list | None] = mapped_column(JSON)
    aplus_summary: Mapped[str | None] = mapped_column(Text)
    variants: Mapped[dict | None] = mapped_column(JSON)
    estimated_monthly_sales: Mapped[float | None] = mapped_column(Float)
    image_url: Mapped[str | None] = mapped_column(String(1000))
    lifecycle_stage: Mapped[str | None] = mapped_column(String(80))
    feature_tags: Mapped[list | None] = mapped_column(JSON)
    data_source: Mapped[str | None] = mapped_column(String(120))
    confidence: Mapped[str] = mapped_column(String(50), default="low")


class TrendSnapshot(Base, TimestampMixin):
    __tablename__ = "trend_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("search_keywords.id"), index=True)
    source: Mapped[str] = mapped_column(String(100))
    window_days: Mapped[int] = mapped_column(Integer)
    trend_score: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(50))
    evidence_url: Mapped[str | None] = mapped_column(String(1000))
    summary: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(50), default="low")


class CompetitorLink(Base, TimestampMixin):
    __tablename__ = "competitor_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("search_keywords.id"), index=True)
    amazon_product_id: Mapped[int | None] = mapped_column(ForeignKey("amazon_products.id"))
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str | None] = mapped_column(String(700))
    price: Mapped[float | None] = mapped_column(Float)
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None] = mapped_column(Integer)
    asin: Mapped[str | None] = mapped_column(String(30))
    estimated_monthly_sales: Mapped[float | None] = mapped_column(Float)
    image_url: Mapped[str | None] = mapped_column(String(1000))
    differentiation: Mapped[str | None] = mapped_column(Text)


class RiskAssessment(Base, TimestampMixin):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("search_keywords.id"), index=True)
    infringement_risk: Mapped[str] = mapped_column(String(50))
    patent_risk: Mapped[str] = mapped_column(String(50))
    trademark_risk: Mapped[str] = mapped_column(String(50))
    compliance_risk: Mapped[str] = mapped_column(String(50))
    risk_score: Mapped[float] = mapped_column(Float)
    review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    rationale: Mapped[str] = mapped_column(Text)


class ProfitCalculation(Base, TimestampMixin):
    __tablename__ = "profit_calculations"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("search_keywords.id"), index=True)
    catalog_product_id: Mapped[int | None] = mapped_column(ForeignKey("catalog_products.id"))
    selling_price: Mapped[float]
    product_cost: Mapped[float | None]
    referral_fee: Mapped[float]
    fba_fee: Mapped[float]
    inbound_shipping: Mapped[float]
    ppc_buffer: Mapped[float]
    net_margin: Mapped[float]
    margin_rate: Mapped[float]
    confidence: Mapped[str] = mapped_column(String(50), default="estimated")


class SourceEvidence(Base, TimestampMixin):
    __tablename__ = "source_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, index=True)
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    summary: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(50), default="low")


class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("search_keywords.id"), index=True)
    catalog_product_id: Mapped[int | None] = mapped_column(ForeignKey("catalog_products.id"))
    title: Mapped[str] = mapped_column(String(500))
    category: Mapped[str | None] = mapped_column(String(255))
    target_audience: Mapped[str | None] = mapped_column(Text)
    lifecycle_stage: Mapped[str | None] = mapped_column(String(80))
    seasonality: Mapped[str | None] = mapped_column(String(120))
    top_features: Mapped[list | None] = mapped_column(JSON)
    differentiation: Mapped[str | None] = mapped_column(Text)
    demand_score: Mapped[float]
    margin_score: Mapped[float]
    competition_score: Mapped[float]
    catalog_match_score: Mapped[float]
    risk_score: Mapped[float]
    opportunity_score: Mapped[float]
    listing_difficulty: Mapped[str] = mapped_column(String(50))
    risk_level: Mapped[str] = mapped_column(String(50))
    recommended_action: Mapped[str] = mapped_column(String(80))
    confidence: Mapped[str] = mapped_column(String(50), default="low")


class UserNote(Base, TimestampMixin):
    __tablename__ = "user_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)


class SavedOpportunity(Base, TimestampMixin):
    __tablename__ = "saved_opportunities"
    __table_args__ = (UniqueConstraint("opportunity_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50), default="watching")


class SyncJob(Base, TimestampMixin):
    __tablename__ = "sync_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_type: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    payload: Mapped[dict | None] = mapped_column(JSON)
    message: Mapped[str | None] = mapped_column(Text)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120))
    entity_type: Mapped[str | None] = mapped_column(String(80))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
