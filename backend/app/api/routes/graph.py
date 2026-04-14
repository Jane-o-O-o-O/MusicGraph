from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_graph_service
from app.schemas.graph import (
    EntityDetails,
    GraphResponse,
    HealthResponse,
    PathResponse,
    SearchResponse,
)
from app.schemas.graphrag import GraphRagQueryRequest, GraphRagResponse
from app.services.graph_service import GraphService

router = APIRouter(tags=["graph"])

ENTITY_TYPES = ["Person", "Band", "Work", "Album", "Genre"]


@router.get("/health", response_model=HealthResponse)
def health(service: GraphService = Depends(get_graph_service)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        mode="mock" if service.using_mock_data else "neo4j",
    )


@router.get("/search", response_model=SearchResponse)
def search_entities(
    q: str = Query("", max_length=120),
    entity_type: str | None = Query(default=None, alias="type"),
    limit: int = Query(default=20, ge=1, le=50),
    service: GraphService = Depends(get_graph_service),
) -> SearchResponse:
    if entity_type and entity_type not in ENTITY_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported entity type.")

    return SearchResponse(items=service.search(q, entity_type=entity_type, limit=limit))


@router.get("/entities/{entity_id}", response_model=EntityDetails)
def get_entity(
    entity_id: str,
    service: GraphService = Depends(get_graph_service),
) -> EntityDetails:
    entity = service.get_entity(entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found.")
    return entity


@router.get("/graph/{entity_id}", response_model=GraphResponse)
def get_graph(
    entity_id: str,
    depth: int = Query(default=1, ge=1, le=2),
    limit: int = Query(default=50, ge=1, le=100),
    service: GraphService = Depends(get_graph_service),
) -> GraphResponse:
    graph = service.get_graph(entity_id, depth=depth, limit=limit)
    if not graph.nodes:
        raise HTTPException(status_code=404, detail="Entity not found.")
    return graph


@router.get("/path", response_model=PathResponse)
def get_path(
    from_id: str = Query(..., alias="from"),
    to_id: str = Query(..., alias="to"),
    service: GraphService = Depends(get_graph_service),
) -> PathResponse:
    path = service.get_path(from_id, to_id)
    if not path.nodes:
        raise HTTPException(status_code=404, detail="Path not found.")
    return PathResponse(**path.model_dump(), source_id=from_id, target_id=to_id)


@router.post("/graphrag/query", response_model=GraphRagResponse)
def query_graphrag(
    payload: GraphRagQueryRequest,
    service: GraphService = Depends(get_graph_service),
) -> GraphRagResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    return service.answer_question(
        question,
        entity_ids=payload.entity_ids,
        depth=payload.depth,
        max_entities=payload.max_entities,
    )
