from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import RiskAssessment, User

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("")
def list_risks(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return db.query(RiskAssessment).order_by(RiskAssessment.risk_score.desc()).limit(500).all()
