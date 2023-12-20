import pytest
from starlette.datastructures import URL

from src.fish import middleware


def test_build_next_url__no_existing_params():
    assert (
        middleware.build_next_url(URL("http://127.0.0.1:8000/sites"), 0, 10)
        == "http://127.0.0.1:8000/sites?skip=0&limit=10"
    )


def test_build_next_url__existing_params():
    assert (
        middleware.build_next_url(
            URL("http://127.0.0.1:8000/sites?limit=10&skip=0"), 0, 10
        )
        == "http://127.0.0.1:8000/sites?skip=0&limit=10"
    )


class RequestStubb:
    def __init__(self):
        self.url = URL("http://127.0.0.1:8000/sites")


def test_generate_next_url__next_url_not_none():
    assert (
        middleware.generate_next_url(10, 0, RequestStubb(), 100)
        == "http://127.0.0.1:8000/sites?skip=10&limit=10"
    )


def test_generate_next_url__next_url_none():
    assert middleware.generate_next_url(10, 90, RequestStubb(), 100) is None


def test_validate_offset_and_limit__expected_pagination():
    assert middleware.validate_offset_and_limit(
        {"skip": "10", "limit": "10"}, 100
    ) == middleware.PaginationKeys(10, 10)


@pytest.mark.parametrize(
    "params", ({"skip": "101"}, {"limit": "101"}, {"skip": "101", "limit": "10"})
)
def test_validate_offset_and_limit__bad_pagination(params):
    result = middleware.validate_offset_and_limit(params, 100)
    assert result.status_code == 400


def test_validate_offset_and_limit__no_params():
    assert middleware.validate_offset_and_limit({}, 100) == middleware.PaginationKeys(
        limit=10, skip=0
    )


@pytest.mark.parametrize("id", ("1", "00005d07-e9f9-12b0-838c-c1407d4bb709"))
def test_retrieve_query_expected_params__id(id):
    assert middleware.retrieve_query_expected_params(f"/species/{id}") == {}


def test_check_for_bad_params__no_bad_params():
    assert (
        middleware.check_for_bad_params({"limit": 10, "skip": 10}, {"limit", "skip"})
        is None
    )


def test_check_for_bad_params__bad_params():
    result = middleware.check_for_bad_params(
        {"limit": 10, "skip": 10, "where": 1}, {"limit", "skip"}
    )
    assert result.status_code == 400
