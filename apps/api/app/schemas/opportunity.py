from datetime import datetime
from pydantic import BaseModel, Field


class KeywordSearchRequest(BaseModel):
    keywords: list[str] = Field(min_length=1, max_length=50)
    category: str | None = None


class CatalogImportRow(BaseModel):
    sku: str
    name: str
    category: str | None = None
    cost: float | None = None
    sale_price: float | None = None
    inventory: int | None = None
    weight: str | None = None
    dimensions: str | None = None
    variants: dict | None = None
    description: str | None = None
    images: list[str] | None = None
    supplier: str | None = "WestMonth"
    source_url: str | None = None


class OpportunityOut(BaseModel):
    id: int
    title: str
    category: str | None
    demand_score: float
    margin_score: float
    competition_score: float
    catalog_match_score: float
    risk_score: float
    opportunity_score: float
    listing_difficulty: str
    risk_level: str
    recommended_action: str
    confidence: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OpportunityDetail(OpportunityOut):
    target_audience: str | None
    lifecycle_stage: str | None
    seasonality: str | None
    top_features: list | None
    differentiation: str | None
    keyword_id: int
    catalog_product_id: int | None
    competitors: list[dict] = Field(default_factory=list)
    trends: list[dict] = Field(default_factory=list)
    profit: dict | None = None


class NoteIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class SaveOpportunityIn(BaseModel):
    status: str = "watching"
