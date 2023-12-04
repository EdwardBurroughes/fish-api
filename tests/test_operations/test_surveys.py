import uuid

from pytest_mock import MockerFixture
import fish.operations.surveys as surveys
from fish.db.models import DBSurvey
from fish.operations.output_models import SurveyResult


def test_get_all_sites(mocker: MockerFixture):
    expected_dict = dict(
        id=uuid.UUID('8f450462-c91e-48b4-9b04-6e82aacf337f'),
        survey_id=10,
        event_date="20/10/2018",
        event_date_year=2018,
        survey_ranked_easting=1242525,
        survey_ranked_northing=266272,
        species_id=20,
        area_id=uuid.UUID('8f450462-c91e-48b4-9b04-6e82aacf337f'),
        fish_count="1"
    )
    model = DBSurvey(**expected_dict)
    mocker.patch.object(surveys, "get_all", return_value=[model])
    assert surveys.get_all_surveys(0, 10) == [SurveyResult(**expected_dict)]