from pydantic import BaseModel, Field

from app.schemas.graph import GraphResponse, SearchItem


class GraphRagQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=400)
    entity_ids: list[str] = Field(default_factory=list, max_length=8)
    depth: int = Field(default=2, ge=1, le=2)
    max_entities: int = Field(default=5, ge=1, le=8)


class GraphRagEvidence(BaseModel):
    type: str
    text: str


class GraphRagResponse(BaseModel):
    question: str
    answer: str
    mode: str
    matched_entities: list[SearchItem] = Field(default_factory=list)
    evidence: list[GraphRagEvidence] = Field(default_factory=list)
    graph: GraphResponse = Field(default_factory=GraphResponse)
