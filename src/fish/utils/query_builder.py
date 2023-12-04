import uuid
from typing import List, Union

from fastapi import HTTPException

from src.fish.db.engine import DBSession
from src.fish.db.models import Base
from fastapi.responses import JSONResponse


def get_all(sql_model: Base, skip: int, limit: int) -> List[Base]:
    with DBSession() as session:
        return session.query(sql_model).offset(skip).limit(limit).all()


def get_model_count(sql_model: Base) -> int:
    with DBSession() as session:
        return session.query(sql_model).count()


def get_by_id(id: Union[str, int], sql_model: Base) -> Base:
    with DBSession() as session:
        return session.query(sql_model).get(id)


def convert_sql_obj_to_dict(table: Base):
    return {c.name: getattr(table, c.name) for c in table.__table__.columns}


def _validate_paginate_param(
        param: int, upper_bound: int, message: str
) -> JSONResponse:
    if not 0 <= param <= upper_bound:
        return JSONResponse(status_code=404, content={"reason": message})


def get_item_by_id(id: Union[str, int, uuid.UUID], model: Base, result_model):
    item = get_by_id(id, model)
    if item is None:
        raise HTTPException(
            status_code=404, detail=f"Unable to find item with ID {id}"
        )
    return result_model(**convert_sql_obj_to_dict(item))