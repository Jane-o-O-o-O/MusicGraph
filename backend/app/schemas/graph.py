from pydantic import BaseModel, Field


class SearchItem(BaseModel):
    id: str
    name: str
    type: str
    summary: str | None = None


class SearchResponse(BaseModel):
    items: list[SearchItem]


class EntityDetails(BaseModel):
    id: str
    name: str
    type: str
    aliases: list[str] = Field(default_factory=list)
    summary: str | None = None
    meta: dict[str, object] = Field(default_factory=dict)


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    summary: str | None = None
    meta: dict[str, object] = Field(default_factory=dict)


class GraphLink(BaseModel):
    id: str
    source: str
    target: str
    type: str
    meta: dict[str, object] = Field(default_factory=dict)


class GraphResponse(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    links: list[GraphLink] = Field(default_factory=list)


class PathResponse(GraphResponse):
    source_id: str
    target_id: str


class HealthResponse(BaseModel):
    status: str
    mode: str
