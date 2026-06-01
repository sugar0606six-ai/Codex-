from io import BytesIO, StringIO
import pandas as pd
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import Opportunity, User

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
    frame = pd.DataFrame(_rows(db))
    stream = BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name="Opportunities")
    return Response(
        stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=opportunities.xlsx"},
    )
