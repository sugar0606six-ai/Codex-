from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import CompetitorLink, Opportunity, ProfitCalculation, SavedOpportunity, SourceEvidence, TrendSnapshot, User, UserNote
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


@router.get("/{opportunity_id}", response_model=OpportunityDetail)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    item = db.get(Opportunity, opportunity_id)
    if not item:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return item


@router.get("/{opportunity_id}/evidence")
def evidence(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = db.get(Opportunity, opportunity_id)
    if not opp:
        return []
    return db.query(SourceEvidence).filter(SourceEvidence.entity_type == "keyword", SourceEvidence.entity_id == opp.keyword_id).all()


@router.get("/{opportunity_id}/competitors")
def competitors(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = db.get(Opportunity, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return (
        db.query(CompetitorLink)
        .filter(CompetitorLink.keyword_id == opp.keyword_id)
        .order_by(CompetitorLink.review_count.desc().nullslast(), CompetitorLink.rating.desc().nullslast())
        .limit(10)
        .all()
    )


@router.get("/{opportunity_id}/profit")
def profit(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = db.get(Opportunity, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return (
        db.query(ProfitCalculation)
        .filter(ProfitCalculation.keyword_id == opp.keyword_id)
        .order_by(ProfitCalculation.created_at.desc())
        .first()
    )


@router.get("/{opportunity_id}/trends")
def trends(opportunity_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    opp = db.get(Opportunity, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return (
        db.query(TrendSnapshot)
        .filter(TrendSnapshot.keyword_id == opp.keyword_id)
        .order_by(TrendSnapshot.window_days.asc(), TrendSnapshot.created_at.desc())
        .all()
    )


@router.post("/{opportunity_id}/notes")
def add_note(opportunity_id: int, payload: NoteIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    note = UserNote(opportunity_id=opportunity_id, user_id=user.id, body=payload.body)
    db.add(note)
    db.commit()
    return {"id": note.id, "body": note.body}


@router.post("/{opportunity_id}/save")
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
