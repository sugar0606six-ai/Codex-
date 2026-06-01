from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.entities import User


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        email = "admin@westmonth.local"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            db.add(User(email=email, hashed_password=hash_password("ChangeMe123!"), role="admin"))
            db.commit()
            print("Created admin@westmonth.local / ChangeMe123!")
        else:
            print("Admin user already exists")
    finally:
        db.close()


if __name__ == "__main__":
    main()
