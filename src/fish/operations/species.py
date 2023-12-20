from typing import List

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Query, Session

from src.fish.db.models import Base, DBSites, DBSpecies, DBSurvey
from src.fish.operations.output_models import SiteBySpecies, SpeciesResult
from src.fish.utils.query_builder import (
    convert_sql_obj_to_dict,
    get_all,
    get_item_by_id,
)


def get_all_species(db: Session, limit: int, skip: int) -> List[SpeciesResult]:
    species = get_all(db, DBSpecies, skip, limit)
    print(species)
    return [SpeciesResult(**convert_sql_obj_to_dict(row)) for row in species]


def get_species_by_id(db: Session, id: int) -> SpeciesResult:
    return get_item_by_id(db, id, DBSpecies, SpeciesResult)


def retrieve_area_by_species_query_builder(id: int, db: Session) -> Query:
    return (
        db.query(
            DBSites.id,
            DBSites.top_tier_site,
            DBSites.site_parent_name,
            DBSites.site_name,
        )
        .join(DBSurvey, onclause=DBSites.id == DBSurvey.area_id)
        .join(DBSpecies, onclause=DBSurvey.species_id == DBSpecies.id)
        .filter(DBSpecies.id == id)
        .group_by(
            DBSites.id,
            DBSites.top_tier_site,
            DBSites.site_parent_name,
            DBSites.site_name,
        )
    )


def get_sites_by_species_id_count(db: Session, id: int) -> int:
    return retrieve_area_by_species_query_builder(id, db).count()


def get_sites_by_species_id(db: Session, id: int, limit: int, skip: int):
    return (
        retrieve_area_by_species_query_builder(id, db).offset(skip).limit(limit).all()
    )


def get_fish_sites_for_a_species(
    db: Session, id: int, limit: int, skip: int
) -> List[SiteBySpecies]:
    site_count = get_sites_by_species_id_count(db, id)
    if not 0 <= limit <= 100:
        raise HTTPException(
            status_code=404, detail=f"limit of {limit} exceeds max limit of 100"
        )

    if not 0 <= skip <= site_count:
        raise HTTPException(
            status_code=404,
            detail=f"skip of {skip} exceeds total count of {site_count}",
        )

    site_species = get_sites_by_species_id(db, id, limit, skip)
    if not site_species:
        raise HTTPException(
            status_code=404, detail=f"unable to result with species id of {id}"
        )
    return [SiteBySpecies(**dict(res._mapping)) for res in site_species]
