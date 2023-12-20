import uuid

from _pytest.fixtures import fixture
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from test_integration.mock_app_setup import (
    TestingSessionLocal,
    override_get_db,
    populate_table,
)

from main import app
from src.fish import middleware
from src.fish.db.engine import get_db
from src.fish.db.models import DBSites, DBSpecies, DBSurvey

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@fixture
def build_species_data():
    with TestingSessionLocal() as session:
        test_species = [
            DBSpecies(id=1, species_name="salmon", latin_name="fishy-fish"),
            DBSpecies(id=2, species_name="gold fish", latin_name="aurum pisces"),
            DBSpecies(id=3, species_name="ed", latin_name="I am a fish"),
        ]
        populate_table(session, test_species)


@fixture
def build_site_data():
    with TestingSessionLocal() as session:
        test_sites = [
            DBSites(
                id="foo-bar",
                top_tier_site="East Hampshire",
                site_parent_name="Hamble",
                site_name="Frog Mill",
                geo_water_body="GB107042016250",
            ),
        ]
        populate_table(session, test_sites)


@fixture
def build_survey_data(build_species_data, build_site_data):
    with TestingSessionLocal() as session:
        test_surveys = [
            DBSurvey(
                id=uuid.UUID("b2cd2911-147a-402b-a6f5-776f37d8194c"),
                survey_id="1",
                event_date="05/07/2010",
                event_date_year=2017,
                survey_ranked_easting=1222,
                survey_ranked_northing=135353,
                species_id=1,
                area_id="foo-bar",
                fish_count=5,
            ),
            DBSurvey(
                id=uuid.UUID("4dacc6b1-75a7-4eda-8584-31c55829da21"),
                survey_id="1",
                event_date="05/07/2010",
                event_date_year=2017,
                survey_ranked_easting=1222,
                survey_ranked_northing=135353,
                species_id=2,
                area_id="foo-bar",
                fish_count=2,
            ),
        ]
        populate_table(session, test_surveys)


@fixture
def mock_middleware(mocker: MockerFixture):
    mocker.patch.object(middleware, "_get_model_count", return_value=3)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "sites": f"{client.base_url}/sites",
        "species": f"{client.base_url}/species",
        "surveys": f"{client.base_url}/surveys",
    }


def test_species_root_path__200_res(mock_middleware, build_species_data):
    response = client.get("/species")
    data = response.json()["data"]
    assert data == [
        {"id": 1, "species_name": "salmon", "latin_name": "fishy-fish"},
        {"id": 2, "species_name": "gold fish", "latin_name": "aurum pisces"},
        {"id": 3, "species_name": "ed", "latin_name": "I am a fish"},
    ]


def test_species_root_path__200_res_limit(mock_middleware, build_species_data):
    response = client.get("/species", params=[("limit", "1")])
    data = response.json()["data"]
    assert data == [{"id": 1, "species_name": "salmon", "latin_name": "fishy-fish"}]


def test_species_root_path__200_res_skip(mock_middleware, build_species_data):
    response = client.get("/species", params=[("skip", "1")])
    data = response.json()["data"]
    assert data == [
        {"id": 2, "species_name": "gold fish", "latin_name": "aurum pisces"}
    ]


def test_species_path__200_res_skip_and_limit(mock_middleware, build_species_data):
    response = client.get("/species", params=[("skip", "1"), ("limit", "2")])
    data = response.json()["data"]
    assert data == [
        {"id": 2, "species_name": "gold fish", "latin_name": "aurum pisces"},
        {"id": 3, "species_name": "ed", "latin_name": "I am a fish"},
    ]


def test_species_root_path__bad_params(mock_middleware):
    response = client.get("/species", params=[("where", "1")])
    assert response.status_code == 400


def test_species_by_id__200_res(mock_middleware, build_species_data):
    response = client.get("/species/1")
    assert response.json()["data"] == {
        "id": 1,
        "species_name": "salmon",
        "latin_name": "fishy-fish",
    }


def test_species_by_id__bad_id(mock_middleware, build_species_data):
    response = client.get("/species/4")
    assert response.status_code == 404


def test_species_by_id__bad_id_str(mock_middleware, build_species_data):
    response = client.get("/species/foo")
    assert response.status_code == 422


def test_get_species_for_sites(mock_middleware, build_survey_data):
    response = client.get("species/2/sites")
    assert response.json() == [
        {
            "id": "foo-bar",
            "top_tier_site": "East Hampshire",
            "site_parent_name": "Hamble",
            "site_name": "Frog Mill",
        }
    ]


def test_get_species_for_sites__bad_limit(mock_middleware, build_survey_data):
    response = client.get("species/2/sites", params=[("limit", "101")])
    message = response.json()["detail"]
    assert response.status_code == 404
    assert message == "limit of 101 exceeds max limit of 100"


def test_get_species_for_sites__bad_skip(mock_middleware, build_survey_data):
    response = client.get("species/2/sites", params=[("skip", "10")])
    message = response.json()["detail"]
    assert response.status_code == 404
    assert message == "skip of 10 exceeds total count of 1"


def test_get_species_for_sites__no_species(mock_middleware, build_survey_data):
    response = client.get("species/10/sites")
    message = response.json()["detail"]
    assert response.status_code == 404
    assert message == "unable to result with species id of 10"
