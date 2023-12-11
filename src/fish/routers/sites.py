from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.fish.db.engine import get_db
from src.fish.operations.output_models import SiteResult, SpeciesBySite
from src.fish.operations.sites import (
    get_all_sites,
    get_sites_by_id,
    get_species_for_a_site,
)

router = APIRouter()


@router.get("/sites")
def api_get_all_sites(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[SiteResult]:
    return get_all_sites(db, skip, limit)


@router.get("/sites/{id}")
def api_get_sites_by_id(id: str, db: Session = Depends(get_db)) -> SiteResult:
    return get_sites_by_id(db, id)


@router.get("/sites/{id}/species")
def api_get_species_by_site(id: str, db: Session = Depends(get_db)) -> List[SpeciesBySite]:
    return get_species_for_a_site(db, id)
