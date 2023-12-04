from fastapi.exceptions import HTTPException
from typing import List

from sqlalchemy.orm import Query
from src.fish.db.engine import DBSession
from src.fish.db.models import DBSpecies, DBSites, DBSurvey, Base
from src.fish.operations.output_models import SpeciesResult, SiteBySpecies
from src.fish.utils.query_builder import (
    get_all,
    convert_sql_obj_to_dict,
    _validate_paginate_param,
    get_item_by_id,
)


def get_all_species(limit: int, skip: int) -> List[SpeciesResult]:
    species = get_all(DBSpecies, limit, skip)
    return [SpeciesResult(**convert_sql_obj_to_dict(row)) for row in species]


def get_species_by_id(id: int) -> SpeciesResult:
    return get_item_by_id(id, DBSpecies, SpeciesResult)


def retrieve_area_by_species_query_builder(id: int, session: DBSession) -> Query:
    return (
        session.query(
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


def get_sites_by_species_id_count(id: int) -> int:
    with DBSession() as session:
        return retrieve_area_by_species_query_builder(id, session).count()


def get_sites_by_species_id(id: int, limit: int, skip: int):
    with DBSession() as session:
        return (
            retrieve_area_by_species_query_builder(id, session)
            .offset(skip)
            .limit(limit)
            .all()
        )


def get_fish_sites_for_a_species(id: int, limit: int, skip: int) -> List[SiteBySpecies]:
    validate_limit_skip_for_species(id, limit, skip)
    site_species = get_sites_by_species_id(id, limit, skip)
    if site_species is None:
        raise HTTPException(
            status_code=404, detail=f"unable to result with site id of {id}"
        )
    return [SiteBySpecies(**dict(res._mapping)) for res in site_species]


def validate_limit_skip_for_species(id: int, limit: int, skip: int):
    site_count = get_sites_by_species_id_count(id)
    _validate_paginate_param(limit, 100, " limit does not fall between range of 0-100")
    _validate_paginate_param(
        skip, site_count, f"skip does not fall between range of 0-{site_count}"
    )
