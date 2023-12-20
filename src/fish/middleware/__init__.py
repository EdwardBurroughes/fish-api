import json
import urllib.parse
import uuid
from collections import namedtuple
from typing import Optional, Union

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.datastructures import URL, QueryParams

from src.fish.db.engine import DBSession
from src.fish.db.models import Base, DBSites, DBSpecies, DBSurvey
from src.fish.utils.query_builder import (
    PaginationError,
    _validate_paginate_param,
    get_model_count,
)

MODEL_MAP = {"/sites": DBSites, "/surveys": DBSurvey, "/species": DBSpecies}
MAX_LIMIT = 100
PaginationKeys = namedtuple("PaginationKeys", ("limit", "skip"))


def build_next_url(url: URL, skip: int, limit: int) -> str:
    params = {"skip": skip, "limit": limit}
    url = url.remove_query_params(keys=["skip", "limit"])
    parsed_params = urllib.parse.urlencode(params)
    return f"{url}?{parsed_params}"


def validate_offset_and_limit(
    query_params: QueryParams, count: int
) -> Union[PaginationKeys, JSONResponse]:
    skip = query_params.get("skip", "0")
    limit = query_params.get("limit", "10")

    try:
        _validate_paginate_param(
            int(skip), count, f"skip of {skip} outside of bounds {0} - {count}"
        )
        _validate_paginate_param(
            int(limit), MAX_LIMIT, f"limit of {limit} outside of bounds {0} - {100}"
        )
        return PaginationKeys(limit=int(limit), skip=int(skip))
    except PaginationError as e:
        return JSONResponse(status_code=400, content={"reason": str(e)})


def generate_next_url(
    cur_limit: int, cur_skip: int, request: Request, total_count: int
) -> Optional[str]:
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
    with DBSession() as session:
        return get_model_count(session, model)


async def wrap_response_with_pagination_results(request: Request, call_next):
    response = await call_next(request)
    model = MODEL_MAP.get(request.url.path)
    if model is not None and response.status_code == 200:
        total_count = _get_model_count(model)
        page = validate_offset_and_limit(request.query_params, total_count)
        # bit of a smell but you can't raise HTTPExceptions in fast api middleware
        if isinstance(page, JSONResponse):
            return page
        next_url = generate_next_url(page.limit, page.skip, request, total_count)
        return await wrap_response_in_meta_data(
            response, total_count=total_count, next_url=next_url
        )
    return response


def is_valid_uuid(id: str):
    try:
        uuid.UUID(id)
        return True
    except ValueError:
        return False


def retrieve_query_expected_params(path: str) -> set:
    expected_params = {"limit", "skip"}
    paths = path.split("/")
    paths_last = paths[len(paths) - 1]
    if paths_last.isdigit() or is_valid_uuid(paths_last):
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
    if path != "/" and request.query_params:
        expected_params = retrieve_query_expected_params(path)
        res = check_for_bad_params(request.query_params, expected_params)
        if res:
            return res

    return await call_next(request)
