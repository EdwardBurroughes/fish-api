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
def mock_middleware(mocker: MockerFixture):
    mocker.patch.object(middleware, "_get_model_count", return_value=2)


@fixture
def build_species_data():
    with TestingSessionLocal() as session:
        test_species = [
            DBSpecies(id=1, species_name="salmon", latin_name="fishy-fish"),
        ]
        populate_table(session, test_species)


@fixture
def build_site_data():
    with TestingSessionLocal() as session:
        test_sites = [
            DBSites(
                id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
                top_tier_site="East Hampshire",
                site_parent_name="kipper",
                site_name="Mill",
                geo_water_body="GB107042016250",
            ),
            DBSites(
                id="01e8c83d-be5a-4e24-9039-4f4334e80a1c",
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
                event_date="05/07/2017",
                event_date_year=2017,
                survey_ranked_easting=1222,
                survey_ranked_northing=135353,
                species_id=1,
                area_id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
                fish_count=5,
            ),
            DBSurvey(
                id=uuid.UUID("4dacc6b1-75a7-4eda-8584-31c55829da21"),
                survey_id="1",
                event_date="05/07/2016",
                event_date_year=2016,
                survey_ranked_easting=1222,
                survey_ranked_northing=135353,
                species_id=1,
                area_id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
                fish_count=2,
            ),
        ]
        populate_table(session, test_surveys)


def test_get_all_sites__200_res(mock_middleware, build_site_data):
    res = client.get("/sites")
    data = res.json()["data"]
    assert data == [
        dict(
            id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
            top_tier_site="East Hampshire",
            site_parent_name="kipper",
            site_name="Mill",
            geo_water_body="GB107042016250",
        ),
        dict(
            id="01e8c83d-be5a-4e24-9039-4f4334e80a1c",
            top_tier_site="East Hampshire",
            site_parent_name="Hamble",
            site_name="Frog Mill",
            geo_water_body="GB107042016250",
        ),
    ]


def test_get_all_sites__limit(mock_middleware, build_site_data):
    res = client.get("/sites?limit=1")
    data = res.json()["data"]
    assert data == [
        dict(
            id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
            top_tier_site="East Hampshire",
            site_parent_name="kipper",
            site_name="Mill",
            geo_water_body="GB107042016250",
        )
    ]


def test_get_all_sites__skip(mock_middleware, build_site_data):
    res = client.get("/sites?skip=1")
    data = res.json()["data"]
    assert data == [
        dict(
            id="01e8c83d-be5a-4e24-9039-4f4334e80a1c",
            top_tier_site="East Hampshire",
            site_parent_name="Hamble",
            site_name="Frog Mill",
            geo_water_body="GB107042016250",
        )
    ]


def test_get_all_sites__bad_skip(mock_middleware, build_site_data):
    res = client.get("/sites?skip=3")
    assert res.status_code == 400


def test_get_all_sites__bad_limit(mock_middleware, build_site_data):
    res = client.get("/sites?limit=101")
    assert res.status_code == 400


def test_api_get_sites_by_id(mock_middleware, build_site_data):
    res = client.get("/sites/01e8c83d-be5a-4e24-9039-4f4334e80a1b")
    assert res.json() == dict(
        id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
        top_tier_site="East Hampshire",
        site_parent_name="kipper",
        site_name="Mill",
        geo_water_body="GB107042016250",
    )


def test_test_api_get_sites_by_id__bad_id(mock_middleware, build_site_data):
    res = client.get("/sites/01e8c83d-be5a-4e24-9039-4f4334e80et2")
    assert res.status_code == 404


def test_api_get_species_by_site__200_res(mock_middleware, build_survey_data):
    res = client.get("/sites/01e8c83d-be5a-4e24-9039-4f4334e80a1b/species")
    assert res.json()[0] == {
        "species_name": "salmon",
        "newest_year_recorded": 2017,
        "oldest_year_recorded": 2016,
        "total_count": 7,
    }


def test_api_get_fish_species_for_a_site__404_with_bad_id(
    mock_middleware, build_survey_data
):
    res = client.get("/sites/01e8c93a-be5a-4e10-9039-4f4554e80b1c/species")
    assert res.status_code == 404
