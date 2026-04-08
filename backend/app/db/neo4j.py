from collections.abc import Iterable

from neo4j import GraphDatabase
from neo4j.graph import Node, Path, Relationship

from app.schemas.graph import EntityDetails, GraphLink, GraphNode, GraphResponse, SearchItem

RESERVED_NODE_FIELDS = {"id", "name", "type", "aliases", "summary"}


def _serialize_value(value):
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if hasattr(value, "iso_format"):
        return value.iso_format()
    return value


def _node_to_graph_node(node: Node) -> GraphNode:
    props = dict(node)
    node_type = props.get("type") or next(iter(node.labels), "Entity")
    meta = {
        key: _serialize_value(value)
        for key, value in props.items()
        if key not in RESERVED_NODE_FIELDS
    }
    return GraphNode(
        id=props["id"],
        label=props.get("name", props["id"]),
        type=node_type,
        summary=props.get("summary"),
        meta=meta,
    )


def _node_to_entity(node: Node) -> EntityDetails:
    props = dict(node)
    node_type = props.get("type") or next(iter(node.labels), "Entity")
    meta = {
        key: _serialize_value(value)
        for key, value in props.items()
        if key not in RESERVED_NODE_FIELDS
    }
    return EntityDetails(
        id=props["id"],
        name=props.get("name", props["id"]),
        type=node_type,
        aliases=_serialize_value(props.get("aliases", [])),
        summary=props.get("summary"),
        meta=meta,
    )


def _relationship_to_graph_link(
    relationship: Relationship,
    start_node: Node,
    end_node: Node,
) -> GraphLink:
    props = dict(relationship)
    rel_type = relationship.type
    source_id = start_node["id"]
    target_id = end_node["id"]
    link_id = f"{source_id}__{rel_type}__{target_id}"
    return GraphLink(
        id=link_id,
        source=source_id,
        target=target_id,
        type=rel_type,
        meta={key: _serialize_value(value) for key, value in props.items()},
    )


class Neo4jGraphRepository:
    def __init__(
        self,
        *,
        uri: str,
        username: str,
        password: str,
        database: str,
    ) -> None:
        self._database = database
        self._driver = GraphDatabase.driver(uri, auth=(username, password))

    def verify_connectivity(self) -> None:
        self._driver.verify_connectivity()

    def close(self) -> None:
        self._driver.close()

    def search(self, query: str, *, entity_type: str | None, limit: int) -> list[SearchItem]:
        label_clause = f":{entity_type}" if entity_type else ""

        if query.strip():
            cypher = f"""
            MATCH (n{label_clause})
            WHERE toLower(n.name) CONTAINS toLower($query)
               OR any(alias IN coalesce(n.aliases, []) WHERE toLower(alias) CONTAINS toLower($query))
            RETURN n
            ORDER BY coalesce(n.popularity, 0) DESC, n.name ASC
            LIMIT $limit
            """
            params = {"query": query.strip(), "limit": limit}
        else:
            cypher = f"""
            MATCH (n{label_clause})
            RETURN n
            ORDER BY coalesce(n.popularity, 0) DESC, n.name ASC
            LIMIT $limit
            """
            params = {"limit": limit}

        with self._driver.session(database=self._database) as session:
            records = session.run(cypher, params)
            items: list[SearchItem] = []
            for record in records:
                node = record["n"]
                props = dict(node)
                items.append(
                    SearchItem(
                        id=props["id"],
                        name=props.get("name", props["id"]),
                        type=props.get("type") or next(iter(node.labels), "Entity"),
                        summary=props.get("summary"),
                    )
                )
            return items

    def get_entity(self, entity_id: str) -> EntityDetails | None:
        cypher = """
        MATCH (n {id: $entity_id})
        RETURN n
        LIMIT 1
        """
        with self._driver.session(database=self._database) as session:
            record = session.run(cypher, {"entity_id": entity_id}).single()
            if record is None:
                return None
            return _node_to_entity(record["n"])

    def get_graph(self, entity_id: str, *, depth: int, limit: int) -> GraphResponse:
        cypher = f"""
        MATCH p = (center {{id: $entity_id}})-[*1..{depth}]-(neighbor)
        RETURN p
        LIMIT $limit
        """
        with self._driver.session(database=self._database) as session:
            records = session.run(cypher, {"entity_id": entity_id, "limit": limit})
            return self._paths_to_graph(records)

    def get_path(self, source_id: str, target_id: str, *, max_hops: int) -> GraphResponse:
        cypher = f"""
        MATCH (source {{id: $source_id}}), (target {{id: $target_id}})
        MATCH p = shortestPath((source)-[*..{max_hops}]-(target))
        RETURN p
        LIMIT 1
        """
        with self._driver.session(database=self._database) as session:
            records = session.run(
                cypher,
                {"source_id": source_id, "target_id": target_id},
            )
            return self._paths_to_graph(records)

    @staticmethod
    def _paths_to_graph(records: Iterable) -> GraphResponse:
        node_map: dict[str, GraphNode] = {}
        link_map: dict[str, GraphLink] = {}

        for record in records:
            path: Path | None = record.get("p")
            if path is None:
                continue

            for node in path.nodes:
                graph_node = _node_to_graph_node(node)
                node_map[graph_node.id] = graph_node

            for index, relationship in enumerate(path.relationships):
                start_node = path.nodes[index]
                end_node = path.nodes[index + 1]
                graph_link = _relationship_to_graph_link(relationship, start_node, end_node)
                link_map[graph_link.id] = graph_link

        return GraphResponse(nodes=list(node_map.values()), links=list(link_map.values()))
