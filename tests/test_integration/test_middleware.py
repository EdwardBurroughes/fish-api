import uuid

import pytest
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

SPECIES_EXPECTED = {
    "total_count": 1,
    "next_url": None,
    "data": [{"id": 1, "species_name": "salmon", "latin_name": "fishy-fish"}],
}
SITES_EXPECTED = {
    "total_count": 1,
    "next_url": None,
    "data": [
        {
            "id": "01e8c83d-be5a-4e24-9039-4f4334e80a1c",
            "top_tier_site": "East Hampshire",
            "site_parent_name": "Hamble",
            "site_name": "Frog Mill",
            "geo_water_body": "GB107042016250",
        }
    ],
}
SURVEYS_EXPECTED = {
    "total_count": 1,
    "next_url": None,
    "data": [
        {
            "id": "01e8c83d-be5a-4e24-9039-4f4334e80a1c",
            "top_tier_site": "East Hampshire",
            "site_parent_name": "Hamble",
            "site_name": "Frog Mill",
            "geo_water_body": "GB107042016250",
        }
    ],
}


@fixture
def mock_get_count(mocker: MockerFixture):
    mocker.patch.object(middleware, "_get_model_count", return_value=1)


@fixture
def build_species_data():
    with TestingSessionLocal() as session:
        test_species = [
            DBSpecies(id=1, species_name="salmon", latin_name="fishy-fish"),
            DBSpecies(id=2, species_name="salmon", latin_name="fishy-fish"),
            DBSpecies(id=3, species_name="salmon", latin_name="fishy-fish"),
        ]
        populate_table(session, test_species)


@fixture
def build_data():
    with TestingSessionLocal() as session:
        test_species = [
            DBSpecies(id=1, species_name="salmon", latin_name="fishy-fish"),
            DBSites(
                id="01e8c83d-be5a-4e24-9039-4f4334e80a1c",
                top_tier_site="East Hampshire",
                site_parent_name="Hamble",
                site_name="Frog Mill",
                geo_water_body="GB107042016250",
            ),
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
        ]
        populate_table(session, test_species)


@pytest.mark.parametrize(
    "endpoint, expected",
    (
        ("/species", SPECIES_EXPECTED),
        ("/sites", SITES_EXPECTED),
        ("/species", SPECIES_EXPECTED),
    ),
)
def test_wrap_response_with_pagination_results__models_to_wrap(
    mock_get_count, build_data, endpoint, expected
):
    res = client.get(endpoint)
    assert res.json() == expected


def test_wrap_response_with_pagination_results__no_wrap(mock_get_count, build_data):
    res = client.get("/species/1")
    assert res.json() == {"id": 1, "species_name": "salmon", "latin_name": "fishy-fish"}


def test_wrap_response_with_pagination_results__next_url(mocker, build_species_data):
    mocker.patch.object(middleware, "_get_model_count", return_value=3)
    res = client.get("/species?limit=1&skip=0")
    next_url = res.json()["next_url"]
    res_two = client.get(next_url)
    assert res_two.json() == {
        "total_count": 3,
        "next_url": "http://testserver/species?skip=2&limit=1",
        "data": [{"id": 2, "species_name": "salmon", "latin_name": "fishy-fish"}],
    }


def test_wrap_response_with_pagination_results__bad_limit(mocker, build_species_data):
    mocker.patch.object(middleware, "_get_model_count", return_value=3)
    res = client.get(f"/species?limit=101")
    assert res.status_code == 400


def test_wrap_response_with_pagination_results__bad_skip(mocker, build_species_data):
    mocker.patch.object(middleware, "_get_model_count", return_value=3)
    res = client.get(f"/species?skip=4")
    assert res.status_code == 400


def test_fail_with_bad_query_params__bad_params(mock_get_count, build_species_data):
    res = client.get("/species?where=1")
    assert res.status_code == 400
    assert res.json() == {"details": "Unexpected query parameters: {'where'}"}
