from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from src.fish import middleware
from src.fish.db.engine import get_db
from src.fish.db.models import Base, DBSpecies
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # in memory database
    poolclass=StaticPool,
    echo=True
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "sites": f"{client.base_url}/sites",
        "species": f"{client.base_url}/species",
        "surveys": f"{client.base_url}/surveys",
    }


def test_species_root_path__200_res(mocker: MockerFixture):
    with TestingSessionLocal() as session:
        test_species = DBSpecies(id=2, species_name='gold fish', latin_name='aurum pisces')
        session.add(test_species)
        session.commit()

        mocker.patch.object(middleware, "_get_model_count", return_value=2)
        response = client.get("/species")
        print(response.json())

    # response = client.get("/species")
