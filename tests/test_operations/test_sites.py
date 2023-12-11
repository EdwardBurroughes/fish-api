import uuid

import pytest
from pytest_mock import MockerFixture
import fish.operations.sites as sites
from fish.db.models import DBSites
from fish.operations.output_models import SiteResult


def test_get_all_sites(mocker: MockerFixture):
    expected_dict = dict(
        id=uuid.UUID("8f450462-c91e-48b4-9b04-6e82aacf337f"),
        top_tier_site="barnsley",
        site_parent_name="yorkshire",
        site_name="Barnsley-river",
        geo_water_body="1234",
    )
    model = DBSites(**expected_dict)
    mocker.patch.object(sites, "get_all", return_value=[model])
    assert sites.get_all_sites(0, 10) == [SiteResult(**expected_dict)]


def test_get_fish_species_for_a_site__no_response(mocker: MockerFixture):
    mocker.patch.object(sites, "get_species_for_a_site", return_value=None)
    with pytest.raises(sites.HTTPException):
        sites.get_fish_species_for_a_site("not-an-id")
