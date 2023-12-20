from typing import List

from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.fish.db.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


def generate_local_db_session() -> sessionmaker:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        # in memory database
        poolclass=StaticPool,
        echo=True,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


TestingSessionLocal = generate_local_db_session()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def populate_table(session: Session, rows: List[Base]):
    for row in rows:
        session.add(row)
    session.commit()
