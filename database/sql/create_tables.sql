CREATE SCHEMA IF NOT exists public;

CREATE TABLE public.fish_species (
    id INT PRIMARY KEY,
    species_name VARCHAR(100),
    latin_name VARCHAR(100)
);

CREATE TABLE public.fish_sites (
    id VARCHAR PRIMARY KEY,
    top_tier_site VARCHAR(256),
    site_parent_name VARCHAR(256),
    site_name VARCHAR(256),
    geo_water_body VARCHAR(100)
);

CREATE TABLE public.fish_survey (
    id uuid PRIMARY KEY,
    survey_id int,
    event_date VARCHAR,
    event_date_year int,
    survey_ranked_easting int,
    survey_ranked_northing int,
    species_id int,
    area_id uuid,
    fish_count VARCHAR
);

COPY public.fish_survey (id, survey_id, event_date, event_date_year, survey_ranked_easting, survey_ranked_northing, species_id, area_id, fish_count)
FROM '/docker-entrypoint-initdb.d/data/fish_survey.csv' DELIMITER ',' CSV HEADER;

COPY public.fish_species (id, species_name, latin_name)
FROM '/docker-entrypoint-initdb.d/data/species_table.csv' DELIMITER ',' CSV HEADER;

COPY public.fish_sites (id, top_tier_site, site_parent_name, site_name, geo_water_body)
FROM '/docker-entrypoint-initdb.d/data/fish_sites.csv' DELIMITER ',' CSV HEADER;

