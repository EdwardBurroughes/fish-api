import json
from collections import namedtuple
from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.datastructures import QueryParams, URL
import urllib.parse

from src.fish.db.engine import DBSession
from src.fish.db.models import DBSites, DBSurvey, DBSpecies, Base
from src.fish.utils.query_builder import get_model_count, _validate_paginate_param

MODEL_MAP = {"/sites": DBSites, "/survey": DBSurvey, "/species": DBSpecies}
MAX_LIMIT = 100
PaginationKeys = namedtuple("PaginationKeys", ("limit", "skip"))


def build_next_url(url: URL, skip: int, limit: int) -> str:
    params = {"skip": skip, "limit": limit}
    url = url.remove_query_params(keys=["skip", "limit"])
    parsed_params = urllib.parse.urlencode(params)
    return f"{url}?{parsed_params}"


def validate_offset_and_limit(query_params: QueryParams, count: int) -> PaginationKeys:
    skip = query_params.get("skip")
    limit = query_params.get("limit")

    if skip and limit:
        _validate_paginate_param(
            int(skip), count, f"skip of {skip} outside of bounds {0} - {count}"
        )
        _validate_paginate_param(
            int(limit), MAX_LIMIT, f"limit of {limit} outside of bounds {0} - {100}"
        )
        result = PaginationKeys(limit=int(limit), skip=int(skip))
    else:
        # Weirdly default values don't show up in the request query params,
        # if query params are not explicitly set in the URL!!
        result = PaginationKeys(10, 0)

    return result


def generate_next_url(cur_limit, cur_skip, request, total_count) -> Optional[str]:
    skip = cur_skip + cur_limit
    next_skip = None if total_count <= skip else skip
    if next_skip:
        return build_next_url(request.url, next_skip, cur_limit)


async def wrap_response_in_meta_data(response, total_count: int, next_url: str):
    response_data = b"".join([i async for i in response.body_iterator]).decode()
    data = json.loads(response_data)
    return JSONResponse(
        status_code=response.status_code,
        content={"total_count": total_count, "next_url": next_url, "data": data},
    )


def _get_model_count(model: Base):
    # simple wrapper as you can't use Depends in your own functions
    with DBSession() as session:
        return get_model_count(session, model)


async def wrap_response_with_pagination_results(request: Request, call_next):
    response = await call_next(request)
    model = MODEL_MAP.get(request.url.path)
    if model is not None:
        total_count = _get_model_count(model)
        page = validate_offset_and_limit(request.query_params, total_count)
        next_url = generate_next_url(page.limit, page.skip, request, total_count)
        return await wrap_response_in_meta_data(
            response, total_count=total_count, next_url=next_url
        )
    return response


def retrieve_query_expected_params(path: str) -> set:
    # currently only limit and offset query params,
    # logic will need to be smarter when this changes
    expected_params = {"limit", "skip"}
    paths = path.split("/")
    paths_last = paths[len(paths) - 1]
    if paths_last.isdigit():
        expected_params = {}
    return expected_params


def check_for_bad_params(
    received_query_params: QueryParams, expected_params: set
) -> JSONResponse:
    unexpected_params = set(received_query_params.keys()) - expected_params
    if unexpected_params:
        return JSONResponse(
            status_code=400,
            content={"details": f"Unexpected query parameters: {unexpected_params}"},
        )


async def fail_with_bad_query_params(request: Request, call_next):
    path = request.url.path
    if path != "/":
        expected_params = retrieve_query_expected_params(path)
        check_for_bad_params(request.query_params, expected_params)

    return await call_next(request)
