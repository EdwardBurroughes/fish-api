from urllib.parse import urljoin

from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from src.fish.db.engine import Creds, init_db
from src.fish.middleware import (
    fail_with_bad_query_params,
    wrap_response_with_pagination_results,
)
from src.fish.routers.sites import router as sites_router
from src.fish.routers.species import router as species_router
from src.fish.routers.surverys import router as surveys_router

app = FastAPI()
AVAILABLE_PATHS = ("sites", "species", "surveys")


# FINISH unit tests for each route + add pre-commit
# Add readme


def get_creds() -> Creds:
    return dotenv_values(".env")


@app.on_event("startup")
async def startup_event():
    creds = get_creds()
    init_db(creds)


@app.get("/")
async def home(request: Request):
    return JSONResponse(
        status_code=200,
        content={path: urljoin(str(request.url), path) for path in AVAILABLE_PATHS},
    )


app.include_router(router=species_router)
app.include_router(router=sites_router)
app.include_router(router=surveys_router)
app.middleware("http")(fail_with_bad_query_params)
app.middleware("http")(wrap_response_with_pagination_results)
