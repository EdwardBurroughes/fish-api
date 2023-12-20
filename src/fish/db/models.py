from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DBSpecies(Base):
    __tablename__ = "fish_species"
    id = Column(Integer, primary_key=True)
    species_name = Column(String(100), nullable=False)
    latin_name = Column(String(100))


class DBSites(Base):
    __tablename__ = "fish_sites"
    id = Column(String, primary_key=True)
    top_tier_site = Column(String(256))
    site_parent_name = Column(String(256))
    site_name = Column(String(256))
    geo_water_body = Column(String(100))


class DBSurvey(Base):
    __tablename__ = "fish_survey"
    id = Column(Uuid, primary_key=True)
    survey_id = Column(Integer, nullable=False)
    event_date = Column(String)
    event_date_year = Column(Integer)
    survey_ranked_easting = Column(Integer)
    survey_ranked_northing = Column(Integer)
    species_id = Column(Integer, ForeignKey("fish_species.id"))
    species = relationship(DBSpecies)
    area_id = Column(String, ForeignKey("fish_sites.id"))
    area = relationship(DBSites)
    fish_count = Column(String)
