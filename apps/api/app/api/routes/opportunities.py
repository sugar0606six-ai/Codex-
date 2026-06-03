from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import (
    AmazonProduct,
    CompetitorLink,
    Opportunity,
    ProfitCalculation,
    SavedOpportunity,
    SourceEvidence,
    TrendSnapshot,
    User,
    UserNote,
)
from app.schemas.opportunity import KeywordSearchRequest, NoteIn, OpportunityDetail, OpportunityOut, SaveOpportunityIn
from app.services.analyzer import OpportunityAnalyzer

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("/analyze", response_model=list[OpportunityOut])
async def analyze(payload: KeywordSearchRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    analyzer = OpportunityAnalyzer()
    results = []
    for keyword in payload.keywords:
        results.append(await analyzer.analyze_keyword(db, keyword, payload.category, user.id))
    return results


@router.get("", response_model=list[OpportunityOut])
def list_opportunities(
    q: str | None = None,
    action: str | None = None,
    risk: str | None = None,
    min_score: float = Query(default=0, ge=0, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    query = db.query(Opportunity).filter(Opportunity.opportunity_score >= min_score)
    if q:
        query = query.filter(Opportunity.title.ilike(f"%{q}%"))
    if action:
        query = query.filter(Opportunity.recommended_action == action)
    if risk:
        query = query.filter(Opportunity.risk_level == risk)
    return query.order_by(Opportunity.opportunity_score.desc(), Opportunity.created_at.desc()).limit(300).all()


@router.get("/_routes")
def opportunity_routes(_: User = Depends(current_user)):
    return {
        "routes": [
            "/api/v1/opportunities/{id}",
            "/api/v1/opportunities/{id}/evidence",
            "/api/v1/opportunities/{id}/competitors",
            "/api/v1/opportunities/{id}/trends",
            "/api/v1/opportunities/{id}/profit",
        ]
    }


def _get_opportunity_or_404(db: Session, opportunity_id: int) -> Opportunity:
    item = db.get(Opportunity, opportunity_id)
    if not item:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return item


def _competitor_rows(db: Session, opp: Opportunity) -> list[dict]:
    rows = (
        db.query(CompetitorLink, AmazonProduct)
        .outerjoin(AmazonProduct, AmazonProduct.id == CompetitorLink.amazon_product_id)
        .filter(CompetitorLink.keyword_id == opp.keyword_id)
        .order_by(CompetitorLink.review_count.desc().nullslast(), CompetitorLink.rating.desc().nullslast())
        .limit(10)
        .all()
    )
    return [
        {
            "id": link.id,
            "amazon_product_id": link.amazon_product_id,
            "asin": link.asin or (product.asin if product else None),
            "title": link.title or (product.title if product else None),
            "url": link.url or (product.listing_url if product else None),
            "price": link.price if link.price is not None else (product.price if product else None),
            "rating": link.rating if link.rating is not None else (product.rating if product else None),
            "review_count": link.review_count if link.review_count is not None else (product.review_count if product else None),
            "estimated_monthly_sales": (
                link.estimated_monthly_sales
                if link.estimated_monthly_sales is not None
                else (product.estimated_monthly_sales if product else None)
            ),
            "image_url": link.image_url or (product.image_url if product else None),
            "differentiation": link.differentiation,
            "data_source": product.data_source if product else None,
            "confidence": product.confidence if product else None,
            "created_at": link.created_at,
        }
        for link, product in rows
    ]


def _trend_rows(db: Session, opp: Opportunity) -> list[TrendSnapshot]:
    return list(
        db.query(TrendSnapshot)
        .filter(TrendSnapshot.keyword_id == opp.keyword_id, TrendSnapshot.window_days.in_([30, 60]))
        .order_by(TrendSnapshot.window_days.asc(), TrendSnapshot.created_at.desc())
        .all()
    )


def _profit_row(db: Session, opp: Opportunity) -> ProfitCalculation | None:
    return (
        db.query(ProfitCalculation)
        .filter(ProfitCalculation.keyword_id == opp.keyword_id)
        .order_by(ProfitCalculation.created_at.desc())
        .first()
    )


@router.get("/{opportunity_id:int}/competitors")
def competitors(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = _get_opportunity_or_404(db, opportunity_id)
    return _competitor_rows(db, opp)


@router.get("/{opportunity_id:int}/trends")
def trends(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = _get_opportunity_or_404(db, opportunity_id)
    return _trend_rows(db, opp)


@router.get("/{opportunity_id:int}/profit")
def profit(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = _get_opportunity_or_404(db, opportunity_id)
    return _profit_row(db, opp)


@router.get("/{opportunity_id:int}", response_model=OpportunityDetail)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = _get_opportunity_or_404(db, opportunity_id)
    return {
        "id": opp.id,
        "title": opp.title,
        "category": opp.category,
        "demand_score": opp.demand_score,
        "margin_score": opp.margin_score,
        "competition_score": opp.competition_score,
        "catalog_match_score": opp.catalog_match_score,
        "risk_score": opp.risk_score,
        "opportunity_score": opp.opportunity_score,
        "listing_difficulty": opp.listing_difficulty,
        "risk_level": opp.risk_level,
        "recommended_action": opp.recommended_action,
        "confidence": opp.confidence,
        "created_at": opp.created_at,
        "target_audience": opp.target_audience,
        "lifecycle_stage": opp.lifecycle_stage,
        "seasonality": opp.seasonality,
        "top_features": opp.top_features,
        "differentiation": opp.differentiation,
        "keyword_id": opp.keyword_id,
        "catalog_product_id": opp.catalog_product_id,
        "competitors": _competitor_rows(db, opp),
        "trends": _trend_rows(db, opp),
        "profit": _profit_row(db, opp),
    }


@router.get("/{opportunity_id:int}/evidence")
def evidence(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = _get_opportunity_or_404(db, opportunity_id)
    return db.query(SourceEvidence).filter(SourceEvidence.entity_type == "keyword", SourceEvidence.entity_id == opp.keyword_id).all()


@router.post("/{opportunity_id:int}/notes")
def add_note(opportunity_id: int, payload: NoteIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    note = UserNote(opportunity_id=opportunity_id, user_id=user.id, body=payload.body)
    db.add(note)
    db.commit()
    return {"id": note.id, "body": note.body}


@router.post("/{opportunity_id:int}/save")
def save(opportunity_id: int, payload: SaveOpportunityIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    saved = (
        db.query(SavedOpportunity)
        .filter(SavedOpportunity.opportunity_id == opportunity_id, SavedOpportunity.user_id == user.id)
        .first()
    )
    if saved:
        saved.status = payload.status
    else:
        saved = SavedOpportunity(opportunity_id=opportunity_id, user_id=user.id, status=payload.status)
        db.add(saved)
    db.commit()
    return {"id": saved.id, "status": saved.status}
