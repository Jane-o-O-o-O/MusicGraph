from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.graph import router as graph_router
from app.core.config import get_settings
from app.services.graph_service import GraphService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    graph_service = GraphService(settings=settings)
    graph_service.startup()
    app.state.graph_service = graph_service
    yield
    graph_service.shutdown()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router, prefix=settings.api_prefix)
