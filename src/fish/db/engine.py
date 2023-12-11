from typing import TypedDict
from sqlalchemy import URL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Creds(TypedDict):
    PGPASSWORD: str
    PGUSER: str
    PGDBNAME: str
    PGHOST: str
    PGPORT: int


DBSession = sessionmaker()


def build_conn_string(creds: Creds) -> URL:
    return URL.create(
        "postgresql",
        username=creds["PGUSER"],
        password=creds["PGPASSWORD"],  # plain (unescaped) text
        host=creds["PGHOST"],
        database=creds["PGDBNAME"],
        port=creds["PGPORT"],
    )


def init_db(creds: Creds):
    url = build_conn_string(creds)
    engine = create_engine(url)
    DBSession.configure(bind=engine)


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
