from typing import List

from fastapi import APIRouter

from src.fish.operations.output_models import SurveyResult
from src.fish.operations.surveys import get_all_surveys, get_survey_by_id

router = APIRouter()


@router.get("/surveys")
def api_get_all_species(limit: int = 10, skip: int = 0) -> List[SurveyResult]:
    return get_all_surveys(limit, skip)


@router.get("/surveys/{id}")
def api_get_species_by_id(id: int) -> SurveyResult:
    return get_survey_by_id(id)


