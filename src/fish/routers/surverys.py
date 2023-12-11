from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.fish.db.engine import get_db
from src.fish.operations.output_models import SurveyResult
from src.fish.operations.surveys import get_all_surveys, get_survey_by_id

router = APIRouter()


@router.get("/surveys")
def api_get_all_species(limit: int = 10, skip: int = 0, db: Session = Depends(get_db)) -> List[SurveyResult]:
    return get_all_surveys(db, limit, skip)


@router.get("/surveys/{id}")
def api_get_species_by_id(id: int,  db: Session = Depends(get_db)) -> SurveyResult:
    return get_survey_by_id(db, id)
