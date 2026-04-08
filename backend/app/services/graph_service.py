from collections import deque
from typing import TYPE_CHECKING

from app.core.config import Settings
from app.data.mock_graph import MOCK_NODES, MOCK_RELATIONSHIPS
from app.schemas.graph import EntityDetails, GraphLink, GraphNode, GraphResponse, SearchItem

if TYPE_CHECKING:
    from app.db.neo4j import Neo4jGraphRepository

RESERVED_NODE_FIELDS = {"id", "name", "type", "aliases", "summary"}


def _node_to_graph_node(node: dict[str, object]) -> GraphNode:
    return GraphNode(
        id=str(node["id"]),
        label=str(node["name"]),
        type=str(node["type"]),
        summary=node.get("summary"),
        meta={key: value for key, value in node.items() if key not in RESERVED_NODE_FIELDS},
    )


def _node_to_entity_details(node: dict[str, object]) -> EntityDetails:
    aliases = node.get("aliases", [])
    if not isinstance(aliases, list):
        aliases = []
    return EntityDetails(
        id=str(node["id"]),
        name=str(node["name"]),
        type=str(node["type"]),
        aliases=[str(alias) for alias in aliases],
        summary=node.get("summary"),
        meta={key: value for key, value in node.items() if key not in RESERVED_NODE_FIELDS},
    )


def _relationship_to_graph_link(relationship: dict[str, object]) -> GraphLink:
    source_id = str(relationship["source"])
    target_id = str(relationship["target"])
    rel_type = str(relationship["type"])
    return GraphLink(
        id=f"{source_id}__{rel_type}__{target_id}",
        source=source_id,
        target=target_id,
        type=rel_type,
        meta={
            key: value
            for key, value in relationship.items()
            if key not in {"source", "target", "type"}
        },
    )


class MockGraphRepository:
    def __init__(self) -> None:
        self._nodes = {node["id"]: node for node in MOCK_NODES}
        self._relationships = list(MOCK_RELATIONSHIPS)
        self._adjacency: dict[str, list[dict[str, object]]] = {}
        for relationship in self._relationships:
            self._adjacency.setdefault(str(relationship["source"]), []).append(relationship)
            self._adjacency.setdefault(str(relationship["target"]), []).append(relationship)

    def search(self, query: str, *, entity_type: str | None, limit: int) -> list[SearchItem]:
        normalized = query.strip().lower()
        matches: list[SearchItem] = []
        for node in self._nodes.values():
            if entity_type and node["type"] != entity_type:
                continue

            if normalized:
                haystacks = [str(node["name"]).lower()]
                haystacks.extend(str(alias).lower() for alias in node.get("aliases", []))
                if not any(normalized in item for item in haystacks):
                    continue

            matches.append(
                SearchItem(
                    id=str(node["id"]),
                    name=str(node["name"]),
                    type=str(node["type"]),
                    summary=node.get("summary"),
                )
            )

        return matches[:limit]

    def get_entity(self, entity_id: str) -> EntityDetails | None:
        node = self._nodes.get(entity_id)
        if node is None:
            return None
        return _node_to_entity_details(node)

    def get_graph(self, entity_id: str, *, depth: int, limit: int) -> GraphResponse:
        if entity_id not in self._nodes:
            return GraphResponse()

        visited_nodes = {entity_id}
        queued = deque([(entity_id, 0)])
        node_map = {entity_id: _node_to_graph_node(self._nodes[entity_id])}
        link_map: dict[str, GraphLink] = {}

        while queued:
            current_id, current_depth = queued.popleft()
            if current_depth >= depth:
                continue

            for relationship in self._adjacency.get(current_id, []):
                graph_link = _relationship_to_graph_link(relationship)
                link_map[graph_link.id] = graph_link

                neighbor_id = (
                    str(relationship["target"])
                    if relationship["source"] == current_id
                    else str(relationship["source"])
                )
                if neighbor_id not in visited_nodes:
                    visited_nodes.add(neighbor_id)
                    node_map[neighbor_id] = _node_to_graph_node(self._nodes[neighbor_id])
                    if len(node_map) >= limit:
                        return GraphResponse(
                            nodes=list(node_map.values()),
                            links=list(link_map.values()),
                        )
                    queued.append((neighbor_id, current_depth + 1))

        return GraphResponse(nodes=list(node_map.values()), links=list(link_map.values()))

    def get_path(self, source_id: str, target_id: str) -> GraphResponse:
        if source_id not in self._nodes or target_id not in self._nodes:
            return GraphResponse()

        queue = deque([source_id])
        previous: dict[str, tuple[str, dict[str, object]] | None] = {source_id: None}

        while queue:
            current_id = queue.popleft()
            if current_id == target_id:
                break

            for relationship in self._adjacency.get(current_id, []):
                neighbor_id = (
                    str(relationship["target"])
                    if relationship["source"] == current_id
                    else str(relationship["source"])
                )
                if neighbor_id in previous:
                    continue
                previous[neighbor_id] = (current_id, relationship)
                queue.append(neighbor_id)

        if target_id not in previous:
            return GraphResponse()

        ordered_nodes = []
        ordered_links = []
        cursor = target_id
        while cursor is not None:
            ordered_nodes.append(_node_to_graph_node(self._nodes[cursor]))
            prev_info = previous[cursor]
            if prev_info is None:
                break
            parent_id, relationship = prev_info
            ordered_links.append(_relationship_to_graph_link(relationship))
            cursor = parent_id

        ordered_nodes.reverse()
        ordered_links.reverse()
        return GraphResponse(nodes=ordered_nodes, links=ordered_links)


class GraphService:
    def __init__(self, *, settings: Settings) -> None:
        self._settings = settings
        self._mock_repository = MockGraphRepository()
        self._neo4j_repository: Neo4jGraphRepository | None = None
        self._using_mock_data = settings.use_mock_data

    @property
    def using_mock_data(self) -> bool:
        return self._using_mock_data

    def startup(self) -> None:
        if self._settings.use_mock_data:
            return

        if not all(
            [
                self._settings.neo4j_uri,
                self._settings.neo4j_username,
                self._settings.neo4j_password,
            ]
        ):
            raise RuntimeError("Neo4j settings are incomplete.")

        try:
            from app.db.neo4j import Neo4jGraphRepository
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "The neo4j package is not installed. Run 'pip install -r requirements.txt'."
            ) from exc

        self._neo4j_repository = Neo4jGraphRepository(
            uri=self._settings.neo4j_uri,
            username=self._settings.neo4j_username,
            password=self._settings.neo4j_password,
            database=self._settings.neo4j_database,
        )
        self._neo4j_repository.verify_connectivity()
        self._using_mock_data = False

    def shutdown(self) -> None:
        if self._neo4j_repository is not None:
            self._neo4j_repository.close()

    def search(self, query: str, *, entity_type: str | None, limit: int) -> list[SearchItem]:
        return self._repository.search(query, entity_type=entity_type, limit=limit)

    def get_entity(self, entity_id: str) -> EntityDetails | None:
        return self._repository.get_entity(entity_id)

    def get_graph(self, entity_id: str, *, depth: int, limit: int) -> GraphResponse:
        graph = self._repository.get_graph(entity_id, depth=depth, limit=limit)
        if graph.nodes:
            return graph

        entity = self.get_entity(entity_id)
        if entity is None:
            return GraphResponse()

        return GraphResponse(
            nodes=[
                GraphNode(
                    id=entity.id,
                    label=entity.name,
                    type=entity.type,
                    summary=entity.summary,
                    meta=entity.meta,
                )
            ],
            links=[],
        )

    def get_path(self, source_id: str, target_id: str) -> GraphResponse:
        if self._using_mock_data:
            return self._mock_repository.get_path(source_id, target_id)

        if self._neo4j_repository is None:
            return GraphResponse()
        return self._neo4j_repository.get_path(source_id, target_id, max_hops=6)

    @property
    def _repository(self):
        return self._mock_repository if self._using_mock_data else self._neo4j_repository
