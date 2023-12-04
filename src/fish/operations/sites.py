from fastapi.exceptions import HTTPException
from typing import List

from sqlalchemy import func, Integer
from src.fish.db.engine import DBSession
from src.fish.db.models import DBSites, DBSpecies, DBSurvey
from src.fish.operations.output_models import SiteResult, SpeciesBySite
from src.fish.utils.query_builder import get_all, convert_sql_obj_to_dict, get_item_by_id


def get_all_sites(skip: int, limit: int) -> List[SiteResult]:
    sites = get_all(DBSites, skip, limit)
    return [SiteResult(**convert_sql_obj_to_dict(site)) for site in sites]


def get_sites_by_id(id: str) -> SiteResult:
    return get_item_by_id(id, DBSites, SiteResult)


def get_species_for_a_site(id: str):
    max_func = func.max(DBSurvey.event_date_year).label("newest_year_recorded")
    min_func = func.min(DBSurvey.event_date_year).label("oldest_year_recorded")
    fish_count_converted = func.sum(func.nullif(DBSurvey.fish_count, "").cast(Integer))
    with DBSession() as session:
        return (
            session.query(
                DBSpecies.species_name,
                max_func,
                min_func,
                fish_count_converted.label("total_count"),
            )
                .join(DBSurvey, onclause=DBSurvey.species_id == DBSpecies.id)
                .join(DBSites, onclause=DBSurvey.area_id == DBSites.id)
                .filter(DBSurvey.area_id == id)
                .group_by(DBSpecies.species_name)
                .order_by(fish_count_converted.desc())
                .all()
        )


# TODO - test postive case
def get_fish_species_for_a_site(id: str):
    site_species = get_species_for_a_site(id)
    if site_species is None:
        raise HTTPException(
            status_code=404, detail=f"unable to get species with site id of {id}"
        )
    return [SpeciesBySite(**convert_sql_obj_to_dict(res)) for res in site_species]
