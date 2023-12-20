from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.fish.db.engine import get_db
from src.fish.operations.output_models import SiteBySpecies, SpeciesResult
from src.fish.operations.species import (
    get_all_species,
    get_fish_sites_for_a_species,
    get_species_by_id,
)

router = APIRouter()


@router.get("/species")
def api_get_all_species(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
) -> List[SpeciesResult]:
    return get_all_species(db, limit, skip)


@router.get("/species/{id}")
def api_get_species_by_id(id: int, db: Session = Depends(get_db)) -> SpeciesResult:
    return get_species_by_id(db, id)


@router.get("/species/{id}/sites")
def api_get_species_for_sites(
    id: int, limit: int = 10, skip: int = 0, db: Session = Depends(get_db)
) -> List[SiteBySpecies]:
    return get_fish_sites_for_a_species(db, id, limit, skip)
