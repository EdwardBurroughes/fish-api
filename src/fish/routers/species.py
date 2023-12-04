from typing import List

from fastapi import APIRouter, Request

from src.fish.operations.output_models import SpeciesResult, SiteBySpecies
from src.fish.operations.species import (
    get_all_species,
    get_species_by_id,
    get_fish_sites_for_a_species,
)

router = APIRouter()


@router.get("/species")
def api_get_all_species(limit: int = 10, skip: int = 0) -> List[SpeciesResult]:
    return get_all_species(limit, skip)


@router.get("/species/{id}")
def api_get_species_by_id(id: int) -> SpeciesResult:
    return get_species_by_id(id)


@router.get("/species/{id}/sites")
def api_get_species_for_sites(
    id: int, limit: int = 10, skip: int = 0
) -> List[SiteBySpecies]:
    return get_fish_sites_for_a_species(id, limit, skip)
