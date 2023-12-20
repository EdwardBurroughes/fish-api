import uuid
from typing import Optional

from pydantic import BaseModel


class SpeciesResult(BaseModel):
    id: int
    species_name: str
    latin_name: Optional[str]


class SiteResult(BaseModel):
    id: uuid.UUID
    top_tier_site: str
    site_parent_name: str
    site_name: str
    geo_water_body: str


class SpeciesBySite(BaseModel):
    species_name: str
    newest_year_recorded: int
    oldest_year_recorded: int
    total_count: Optional[int]


class SiteBySpecies(BaseModel):
    id: str
    top_tier_site: str
    site_parent_name: str
    site_name: str


class SurveyResult(BaseModel):
    id: uuid.UUID
    survey_id: int
    event_date_year: int
    survey_ranked_easting: int
    survey_ranked_northing: int
    species_id: int
    area_id: uuid.UUID
    fish_count: str
