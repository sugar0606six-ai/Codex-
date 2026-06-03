from io import BytesIO, StringIO
import pandas as pd
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import CompetitorLink, Opportunity, ProfitCalculation, SourceEvidence, TrendSnapshot, User

router = APIRouter(prefix="/exports", tags=["exports"])


def _rows(db: Session) -> list[dict]:
    items = db.query(Opportunity).order_by(Opportunity.opportunity_score.desc()).all()
    return [
        {
            "title": item.title,
            "category": item.category,
            "demand_score": item.demand_score,
            "margin_score": item.margin_score,
            "competition_score": item.competition_score,
            "catalog_match_score": item.catalog_match_score,
            "risk_score": item.risk_score,
            "opportunity_score": item.opportunity_score,
            "recommended_action": item.recommended_action,
            "confidence": item.confidence,
        }
        for item in items
    ]


def _competitor_rows(db: Session) -> list[dict]:
    rows = (
        db.query(Opportunity, CompetitorLink)
        .join(CompetitorLink, CompetitorLink.keyword_id == Opportunity.keyword_id)
        .order_by(Opportunity.opportunity_score.desc(), CompetitorLink.review_count.desc().nullslast())
        .all()
    )
    return [
        {
            "opportunity": opportunity.title,
            "asin": competitor.asin,
            "title": competitor.title,
            "price": competitor.price,
            "rating": competitor.rating,
            "review_count": competitor.review_count,
            "estimated_monthly_sales": competitor.estimated_monthly_sales,
            "url": competitor.url,
            "differentiation": competitor.differentiation,
        }
        for opportunity, competitor in rows
    ]


def _profit_rows(db: Session) -> list[dict]:
    rows = (
        db.query(Opportunity, ProfitCalculation)
        .join(ProfitCalculation, ProfitCalculation.keyword_id == Opportunity.keyword_id)
        .order_by(Opportunity.opportunity_score.desc())
        .all()
    )
    return [
        {
            "opportunity": opportunity.title,
            "selling_price": profit.selling_price,
            "product_cost": profit.product_cost,
            "referral_fee": profit.referral_fee,
            "fba_fee": profit.fba_fee,
            "inbound_shipping": profit.inbound_shipping,
            "ppc_buffer": profit.ppc_buffer,
            "net_margin": profit.net_margin,
            "margin_rate": profit.margin_rate,
            "confidence": profit.confidence,
        }
        for opportunity, profit in rows
    ]


def _trend_rows(db: Session) -> list[dict]:
    rows = (
        db.query(Opportunity, TrendSnapshot)
        .join(TrendSnapshot, TrendSnapshot.keyword_id == Opportunity.keyword_id)
        .order_by(Opportunity.opportunity_score.desc(), TrendSnapshot.window_days.asc())
        .all()
    )
    return [
        {
            "opportunity": opportunity.title,
            "source": trend.source,
            "window_days": trend.window_days,
            "trend_score": trend.trend_score,
            "direction": trend.direction,
            "evidence_url": trend.evidence_url,
            "confidence": trend.confidence,
        }
        for opportunity, trend in rows
    ]


def _evidence_rows(db: Session) -> list[dict]:
    rows = (
        db.query(Opportunity, SourceEvidence)
        .join(SourceEvidence, SourceEvidence.entity_id == Opportunity.keyword_id)
        .filter(SourceEvidence.entity_type == "keyword")
        .order_by(Opportunity.opportunity_score.desc(), SourceEvidence.created_at.desc())
        .all()
    )
    return [
        {
            "opportunity": opportunity.title,
            "source_name": evidence.source_name,
            "source_url": evidence.source_url,
            "summary": evidence.summary,
            "confidence": evidence.confidence,
            "captured_at": evidence.captured_at,
        }
        for opportunity, evidence in rows
    ]


@router.get("/opportunities.csv")
def export_csv(db: Session = Depends(get_db), _: User = Depends(current_user)):
    frame = pd.DataFrame(_rows(db))
    stream = StringIO()
    frame.to_csv(stream, index=False)
    return Response(
        stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=opportunities.csv"},
    )


@router.get("/opportunities.xlsx")
def export_xlsx(db: Session = Depends(get_db), _: User = Depends(current_user)):
    stream = BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        pd.DataFrame(_rows(db)).to_excel(writer, index=False, sheet_name="Opportunities")
        pd.DataFrame(_competitor_rows(db)).to_excel(writer, index=False, sheet_name="Competitors")
        pd.DataFrame(_profit_rows(db)).to_excel(writer, index=False, sheet_name="Profit")
        pd.DataFrame(_trend_rows(db)).to_excel(writer, index=False, sheet_name="Trends")
        pd.DataFrame(_evidence_rows(db)).to_excel(writer, index=False, sheet_name="Evidence")
    return Response(
        stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=opportunities.xlsx"},
    )
