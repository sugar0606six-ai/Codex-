from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import SyncJob, User

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return db.query(SyncJob).order_by(SyncJob.created_at.desc()).limit(100).all()


@router.post("/schedule")
def schedule_job(job_type: str, db: Session = Depends(get_db), _: User = Depends(current_user)):
    job = SyncJob(job_type=job_type, status="queued", payload={"requested_at": datetime.utcnow().isoformat()})
    db.add(job)
    db.commit()
    return {"id": job.id, "status": job.status}
