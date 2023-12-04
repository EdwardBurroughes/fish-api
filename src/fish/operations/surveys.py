from typing import List
from src.fish.db.models import DBSurvey
from src.fish.operations.output_models import SurveyResult
from src.fish.utils.query_builder import get_all, convert_sql_obj_to_dict, get_item_by_id


def get_all_surveys(limit: int, offset: int) -> List[SurveyResult]:
    surveys = get_all(DBSurvey, limit, offset)
    return [SurveyResult(**convert_sql_obj_to_dict(survey)) for survey in surveys]


def get_survey_by_id(id: int) -> SurveyResult:
    return get_item_by_id(id, DBSurvey, SurveyResult)

