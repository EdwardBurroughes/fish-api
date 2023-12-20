import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture

from src.fish.db.models import DBSpecies
from src.fish.operations.output_models import SpeciesResult
from src.fish.utils import query_builder


def test_validate_paginate_param__exceeds_upper_bound():
    with pytest.raises(query_builder.PaginationError) as e:
        query_builder._validate_paginate_param(101, 100, "it failed")
        assert e.value == "it failed"


def test_convert_sql_obj_to_dict():
    species = DBSpecies(id=1, species_name="salmon", latin_name="fishy-fish")
    assert query_builder.convert_sql_obj_to_dict(species) == {
        "id": 1,
        "species_name": "salmon",
        "latin_name": "fishy-fish",
    }


def test_get_item_by_id(mocker: MockerFixture):
    species = DBSpecies(id=1, species_name="salmon", latin_name="fishy-fish")
    mocker.patch.object(query_builder, "get_by_id", return_value=species)
    assert query_builder.get_item_by_id(
        "foo", 1, DBSpecies, SpeciesResult
    ) == SpeciesResult(id=1, species_name="salmon", latin_name="fishy-fish")


def test_get_item_by_id__no_id(mocker: MockerFixture):
    mocker.patch.object(query_builder, "get_by_id", return_value=None)
    with pytest.raises(HTTPException):
        query_builder.get_item_by_id("foo", 1, DBSpecies, SpeciesResult)
