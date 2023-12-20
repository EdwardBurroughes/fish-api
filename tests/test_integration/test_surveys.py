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
from src.fish.db.models import DBSurvey

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@fixture
def mock_middleware(mocker: MockerFixture):
    mocker.patch.object(middleware, "_get_model_count", return_value=3)


@fixture
def build_surveys_data():
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
                area_id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
                fish_count=5,
            ),
            DBSurvey(
                id=uuid.UUID("4dacc6b1-75a7-4eda-8584-31c55829da21"),
                survey_id="2",
                event_date="05/07/2010",
                event_date_year=2017,
                survey_ranked_easting=1222,
                survey_ranked_northing=135353,
                species_id=3,
                area_id="26c5771b-e091-45e1-9284-e1583083eaad",
                fish_count=2,
            ),
            DBSurvey(
                id=uuid.UUID("4dacc6b1-75a7-4eda-8584-31c55829da22"),
                survey_id="3",
                event_date="05/07/2010",
                event_date_year=2017,
                survey_ranked_easting=1222,
                survey_ranked_northing=135353,
                species_id=2,
                area_id="4566acbc-0e40-4dd8-984f-dfec8bb39172",
                fish_count=2,
            ),
        ]
        populate_table(session, test_surveys)


def test_get_all_survey__200_res(mock_middleware, build_surveys_data):
    response = client.get("/surveys")
    data = response.json()["data"]
    print(data)
    assert data == [
        dict(
            id="b2cd2911-147a-402b-a6f5-776f37d8194c",
            survey_id=1,
            event_date="05/07/2010",
            event_date_year=2017,
            survey_ranked_easting=1222,
            survey_ranked_northing=135353,
            species_id=1,
            area_id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
            fish_count="5",
        ),
        dict(
            id="4dacc6b1-75a7-4eda-8584-31c55829da21",
            survey_id=2,
            event_date="05/07/2010",
            event_date_year=2017,
            survey_ranked_easting=1222,
            survey_ranked_northing=135353,
            species_id=3,
            area_id="26c5771b-e091-45e1-9284-e1583083eaad",
            fish_count="2",
        ),
        dict(
            id="4dacc6b1-75a7-4eda-8584-31c55829da22",
            survey_id=3,
            event_date="05/07/2010",
            event_date_year=2017,
            survey_ranked_easting=1222,
            survey_ranked_northing=135353,
            species_id=2,
            area_id="4566acbc-0e40-4dd8-984f-dfec8bb39172",
            fish_count="2",
        ),
    ]


def test_get_all_surveys__limit(mock_middleware, build_surveys_data):
    response = client.get("/surveys?limit=1")
    data = response.json()["data"]
    assert data == [
        dict(
            id="b2cd2911-147a-402b-a6f5-776f37d8194c",
            survey_id=1,
            event_date_year=2017,
            survey_ranked_easting=1222,
            survey_ranked_northing=135353,
            species_id=1,
            area_id="01e8c83d-be5a-4e24-9039-4f4334e80a1b",
            fish_count="5",
        )
    ]


def test_get_all_surveys__limit_skip(mock_middleware, build_surveys_data):
    response = client.get("/surveys?limit=1&skip=1")
    data = response.json()["data"]
    assert data == [
        dict(
            id="4dacc6b1-75a7-4eda-8584-31c55829da21",
            survey_id=2,
            event_date_year=2017,
            survey_ranked_easting=1222,
            survey_ranked_northing=135353,
            species_id=3,
            area_id="26c5771b-e091-45e1-9284-e1583083eaad",
            fish_count="2",
        ),
    ]


def test_all_surveys__bad_response_when_skip_exceeds_count(
    mock_middleware, build_surveys_data
):
    response = client.get("/surveys?skip=4")
    assert response.status_code == 400


def test_all_surveys__bad_response_when_limit_exceeds_max_count(
    mock_middleware, build_surveys_data
):
    response = client.get("/surveys?limit=101")
    assert response.status_code == 400


def test_api_get_surveys_by_id__200_res(mock_middleware, build_surveys_data):
    response = client.get("/surveys/4dacc6b1-75a7-4eda-8584-31c55829da21")
    data = response.json()
    assert data == dict(
        id="4dacc6b1-75a7-4eda-8584-31c55829da21",
        survey_id=2,
        event_date_year=2017,
        survey_ranked_easting=1222,
        survey_ranked_northing=135353,
        species_id=3,
        area_id="26c5771b-e091-45e1-9284-e1583083eaad",
        fish_count="2",
    )


def test_api_get_surveys_by_id__no_id(mock_middleware, build_surveys_data):
    response = client.get("/surveys/4dacc6b1-75a7-4eda-8584-31c55829ed24")
    assert response.status_code == 404


def test_api_get_surveys_fails__with_bad_params(mock_middleware, build_surveys_data):
    response = client.get("/surveys?hello=world")
    assert response.status_code == 400
