import uuid
from typing import List

from sqlalchemy.orm import Session

from src.fish.db.models import DBSurvey
from src.fish.operations.output_models import SurveyResult
from src.fish.utils.query_builder import (
    convert_sql_obj_to_dict,
    get_all,
    get_item_by_id,
)


def get_all_surveys(db: Session, limit: int, skip: int) -> List[SurveyResult]:
    surveys = get_all(db, DBSurvey, skip, limit)
    return [SurveyResult(**convert_sql_obj_to_dict(survey)) for survey in surveys]


def get_survey_by_id(db: Session, id: uuid.UUID) -> SurveyResult:
    return get_item_by_id(db, id, DBSurvey, SurveyResult)
