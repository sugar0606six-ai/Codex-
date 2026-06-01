from fastapi import APIRouter, Depends
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.entities import CatalogProduct, User
from app.schemas.opportunity import CatalogImportRow

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/import")
def import_catalog(rows: list[CatalogImportRow], db: Session = Depends(get_db), _: User = Depends(current_user)):
    for row in rows:
        stmt = insert(CatalogProduct).values(**row.model_dump()).on_conflict_do_update(
            index_elements=[CatalogProduct.sku],
            set_={key: value for key, value in row.model_dump().items() if key != "sku"},
        )
        db.execute(stmt)
    db.commit()
    return {"imported": len(rows)}


@router.get("")
def list_catalog(q: str | None = None, db: Session = Depends(get_db), _: User = Depends(current_user)):
    query = db.query(CatalogProduct)
    if q:
        query = query.filter((CatalogProduct.name.ilike(f"%{q}%")) | (CatalogProduct.sku.ilike(f"%{q}%")))
    return query.order_by(CatalogProduct.updated_at.desc()).limit(500).all()
