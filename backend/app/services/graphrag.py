import re
from itertools import combinations
from typing import TYPE_CHECKING

from app.schemas.graph import EntityDetails, GraphLink, GraphNode, GraphResponse, SearchItem
from app.schemas.graphrag import GraphRagEvidence, GraphRagResponse
from app.services.llm import RemoteLlmService
from app.services.local_nlp import get_local_nlp_service

if TYPE_CHECKING:
    from app.services.graph_service import GraphService

TYPE_LABELS = {
    "Person": "人物",
    "Band": "乐团",
    "Work": "作品",
    "Album": "专辑",
    "Genre": "流派",
}

RELATION_LABELS = {
    "PERFORMED": "演唱",
    "COMPOSED": "作曲",
    "WROTE_LYRICS_FOR": "作词",
    "MEMBER_OF": "成员",
    "IN_ALBUM": "收录于",
    "HAS_GENRE": "风格",
}

QUESTION_SPLIT_PATTERN = re.compile(
    r"[，。！？、,.!?/:：；;\s]|和|与|跟|以及|还有|什么|哪些|谁|关系|合作|路径|之间|介绍|一下|请问|有|的|是"
)


def _entity_to_search_item(entity: EntityDetails) -> SearchItem:
    return SearchItem(
        id=entity.id,
        name=entity.name,
        type=entity.type,
        summary=entity.summary,
    )


def _merge_graphs(graphs: list[GraphResponse]) -> GraphResponse:
    node_map: dict[str, GraphNode] = {}
    link_map: dict[str, GraphLink] = {}

    for graph in graphs:
        for node in graph.nodes:
            node_map[node.id] = node
        for link in graph.links:
            if link.source in node_map and link.target in node_map:
                link_map[link.id] = link

    valid_links = [
        link
        for link in link_map.values()
        if link.source in node_map and link.target in node_map
    ]
    return GraphResponse(nodes=list(node_map.values()), links=valid_links)


def _build_node_map(graph: GraphResponse) -> dict[str, GraphNode]:
    return {node.id: node for node in graph.nodes}


def _build_adjacency(graph: GraphResponse) -> dict[str, list[GraphLink]]:
    adjacency: dict[str, list[GraphLink]] = {}
    for link in graph.links:
        adjacency.setdefault(link.source, []).append(link)
        adjacency.setdefault(link.target, []).append(link)
    return adjacency


def _link_text(link: GraphLink, node_map: dict[str, GraphNode]) -> str:
    source = node_map.get(link.source)
    target = node_map.get(link.target)
    if source is None or target is None:
        return link.type
    relation = RELATION_LABELS.get(link.type, link.type)
    return f"{source.label} - {relation} -> {target.label}"


def _related_labels(
    graph: GraphResponse,
    focus_id: str,
    relation_types: set[str],
    node_types: set[str] | None = None,
) -> list[str]:
    node_map = _build_node_map(graph)
    labels: list[str] = []
    for link in graph.links:
        if link.type not in relation_types:
            continue
        if link.source == focus_id and link.target in node_map:
            other = node_map[link.target]
        elif link.target == focus_id and link.source in node_map:
            other = node_map[link.source]
        else:
            continue
        if node_types and other.type not in node_types:
            continue
        labels.append(other.label)
    return sorted(set(labels))


def _format_path(graph: GraphResponse) -> str | None:
    if len(graph.nodes) < 2 or not graph.links:
        return None

    node_map = _build_node_map(graph)
    steps: list[str] = []
    for index in range(len(graph.nodes) - 1):
        current = graph.nodes[index]
        nxt = graph.nodes[index + 1]
        link = next(
            (
                candidate
                for candidate in graph.links
                if {candidate.source, candidate.target} == {current.id, nxt.id}
            ),
            None,
        )
        if link is None:
            continue
        relation = RELATION_LABELS.get(link.type, link.type)
        if link.source == current.id and link.target == nxt.id:
            steps.append(f"{current.label} -[{relation}]-> {nxt.label}")
        else:
            steps.append(f"{current.label} <-[{relation}]- {nxt.label}")

    return "；".join(steps) if steps else None


class GraphRagEngine:
    def __init__(self, graph_service: "GraphService", remote_llm: RemoteLlmService) -> None:
        self._graph_service = graph_service
        self._remote_llm = remote_llm
        self._local_nlp = get_local_nlp_service()

    def answer_question(
        self,
        question: str,
        *,
        entity_ids: list[str] | None = None,
        depth: int = 2,
        max_entities: int = 5,
    ) -> GraphRagResponse:
        resolved_entities = self._resolve_entities(
            question,
            entity_ids=entity_ids or [],
            max_entities=max_entities,
        )

        if not resolved_entities:
            return GraphRagResponse(
                question=question,
                answer="当前图谱里没有检索到足够相关的实体，建议直接提到人物、作品、乐团或专辑名称再试一次。",
                mode=self._mode,
                matched_entities=[],
                evidence=[],
                graph=GraphResponse(),
            )

        base_graphs = [
            self._graph_service.get_graph(entity.id, depth=depth, limit=80)
            for entity in resolved_entities
        ]

        path_graphs: list[GraphResponse] = []
        for source, target in list(combinations(resolved_entities[:3], 2)):
            path_graph = self._graph_service.get_path(source.id, target.id)
            if path_graph.nodes:
                path_graphs.append(path_graph)

        merged_graph = _merge_graphs(base_graphs + path_graphs)
        evidence = self._build_evidence(resolved_entities, merged_graph, path_graphs)
        answer = self._generate_answer(question, resolved_entities, merged_graph, path_graphs, evidence)

        return GraphRagResponse(
            question=question,
            answer=answer,
            mode=self._mode,
            matched_entities=[_entity_to_search_item(entity) for entity in resolved_entities],
            evidence=evidence,
            graph=merged_graph,
        )

    @property
    def _mode(self) -> str:
        backend_mode = "mock-graphrag" if self._graph_service.using_mock_data else "neo4j-graphrag"
        if self._remote_llm.available and self._remote_llm.provider:
            backend_mode = f"{backend_mode}+{self._remote_llm.provider}"
        if self._local_nlp.available:
            return f"{backend_mode}+local-nlp"
        return backend_mode

    def _generate_answer(
        self,
        question: str,
        entities: list[EntityDetails],
        graph: GraphResponse,
        path_graphs: list[GraphResponse],
        evidence: list[GraphRagEvidence],
    ) -> str:
        fallback_answer = self._build_answer(question, entities, graph, path_graphs)
        if not self._remote_llm.available:
            return fallback_answer

        try:
            llm_answer = self._build_llm_answer(question, entities, evidence, fallback_answer)
            if self._is_usable_llm_answer(llm_answer):
                return llm_answer
            return fallback_answer
        except Exception:
            return fallback_answer

    @staticmethod
    def _is_usable_llm_answer(answer: str) -> bool:
        normalized = answer.strip()
        if len(normalized) < 12:
            return False

        bad_markers = [
            "原始简介",
            "我翻译",
            "我需要",
            "我可以",
            "证据中",
            "下面",
            "草稿",
            "整理成",
            "不要",
            "项目符号",
        ]
        if any(marker in normalized for marker in bad_markers):
            return False
        return True

    def _build_llm_answer(
        self,
        question: str,
        entities: list[EntityDetails],
        evidence: list[GraphRagEvidence],
        fallback_answer: str,
    ) -> str:
        user_prompt = (
            "请把下面这段图谱问答结果整理成自然、简洁的中文答案。"
            "不能增加新事实，不能删除关键事实，不要解释过程，不要项目符号，不要表情。\n\n"
            f"问题：{question}\n\n"
            f"原始答案：{fallback_answer}"
        )
        system_prompt = "你是 MusicGraph 的中文润色助手，只输出最终答案。"
        return self._remote_llm.generate_answer(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _resolve_entities(
        self,
        question: str,
        *,
        entity_ids: list[str],
        max_entities: int,
    ) -> list[EntityDetails]:
        resolved: list[EntityDetails] = []
        seen_ids: set[str] = set()

        for entity_id in entity_ids:
            entity = self._graph_service.get_entity(entity_id)
            if entity is None or entity.id in seen_ids:
                continue
            resolved.append(entity)
            seen_ids.add(entity.id)

        catalog: list[EntityDetails] = []
        for item in self._graph_service.search("", entity_type=None, limit=100):
            entity = self._graph_service.get_entity(item.id)
            if entity is not None:
                catalog.append(entity)

        lowered_question = question.casefold()
        for entity in catalog:
            aliases = [alias.casefold() for alias in entity.aliases if len(alias.strip()) >= 2]
            candidate_names = [entity.name.casefold(), *aliases]
            if any(name and name in lowered_question for name in candidate_names):
                if entity.id not in seen_ids:
                    resolved.append(entity)
                    seen_ids.add(entity.id)
            if len(resolved) >= max_entities:
                return resolved[:max_entities]

        candidate_terms = self._local_nlp.extract_candidate_terms(question)
        candidate_terms.extend(
            [term for term in QUESTION_SPLIT_PATTERN.split(question) if len(term.strip()) >= 2]
        )
        candidate_terms.append(question.strip())

        for term in sorted(set(candidate_terms), key=len, reverse=True):
            for item in self._graph_service.search(term, entity_type=None, limit=max_entities):
                if item.id in seen_ids:
                    continue
                entity = self._graph_service.get_entity(item.id)
                if entity is None:
                    continue
                resolved.append(entity)
                seen_ids.add(entity.id)
                if len(resolved) >= max_entities:
                    return resolved[:max_entities]

        return resolved[:max_entities]

    def _build_evidence(
        self,
        entities: list[EntityDetails],
        graph: GraphResponse,
        path_graphs: list[GraphResponse],
    ) -> list[GraphRagEvidence]:
        node_map = _build_node_map(graph)
        evidence: list[GraphRagEvidence] = []

        for entity in entities[:3]:
            summary = entity.summary or f"{entity.name} 是图谱中的 {TYPE_LABELS.get(entity.type, entity.type)}。"
            evidence.append(
                GraphRagEvidence(type="entity", text=f"{entity.name}：{summary}")
            )

        for link in graph.links[:5]:
            evidence.append(GraphRagEvidence(type="relation", text=_link_text(link, node_map)))

        for path_graph in path_graphs[:2]:
            path_text = _format_path(path_graph)
            if path_text:
                evidence.append(GraphRagEvidence(type="path", text=path_text))

        return evidence[:8]

    def _build_answer(
        self,
        question: str,
        entities: list[EntityDetails],
        graph: GraphResponse,
        path_graphs: list[GraphResponse],
    ) -> str:
        lowered_question = question.casefold()
        node_map = _build_node_map(graph)
        adjacency = _build_adjacency(graph)

        if len(entities) >= 2 and any(keyword in lowered_question for keyword in ["关系", "合作", "路径", "之间"]):
            for path_graph in path_graphs:
                path_text = _format_path(path_graph)
                if path_text:
                    return (
                        f"基于当前图谱，{entities[0].name} 和 {entities[1].name} 之间存在可解释的关联路径："
                        f"{path_text}。"
                    )

        focus = entities[0]
        focus_links = adjacency.get(focus.id, [])

        if focus.type == "Work" and any(
            keyword in lowered_question for keyword in ["介绍", "作品", "歌曲", "歌", "什么"]
        ):
            performers = _related_labels(graph, focus.id, {"PERFORMED"}, {"Person", "Band"})
            composers = _related_labels(graph, focus.id, {"COMPOSED"}, {"Person"})
            lyricists = _related_labels(graph, focus.id, {"WROTE_LYRICS_FOR"}, {"Person"})
            albums = _related_labels(graph, focus.id, {"IN_ALBUM"}, {"Album"})
            genres = _related_labels(graph, focus.id, {"HAS_GENRE"}, {"Genre"})

            segments = [f"{focus.name} 是一首作品"]
            if focus.summary:
                segments.append(f"简介：{focus.summary}")
            if performers:
                segments.append(f"演唱相关实体：{'、'.join(performers)}")
            if composers:
                segments.append(f"作曲相关人物：{'、'.join(composers)}")
            if lyricists:
                segments.append(f"作词相关人物：{'、'.join(lyricists)}")
            if albums:
                segments.append(f"收录专辑：{'、'.join(albums)}")
            if genres:
                segments.append(f"关联风格：{'、'.join(genres)}")
            return "；".join(segments) + "。"

        if any(keyword in lowered_question for keyword in ["成员"]):
            members = [
                node_map[link.source].label
                for link in graph.links
                if link.type == "MEMBER_OF" and link.target == focus.id and link.source in node_map
            ]
            if members:
                return f"基于当前图谱，{focus.name} 的成员包括：{'、'.join(sorted(set(members)))}。"

        if any(keyword in lowered_question for keyword in ["流派", "风格"]):
            genres = [
                node_map[link.target].label
                for link in graph.links
                if link.type == "HAS_GENRE" and link.source == focus.id and link.target in node_map
            ]
            if genres:
                return f"基于当前图谱，{focus.name} 关联的风格包括：{'、'.join(sorted(set(genres)))}。"

        if any(keyword in lowered_question for keyword in ["专辑"]):
            albums = [
                node_map[link.target].label
                for link in graph.links
                if link.type == "IN_ALBUM" and link.target in node_map
            ]
            related_albums = sorted(set(albums))
            if related_albums:
                return f"基于当前图谱，问题相关的专辑包括：{'、'.join(related_albums)}。"

        if any(keyword in lowered_question for keyword in ["作品", "歌曲", "歌"]):
            works = _related_labels(
                graph,
                focus.id,
                {"PERFORMED", "COMPOSED", "WROTE_LYRICS_FOR"},
                {"Work"},
            )
            if works:
                return f"基于当前图谱，{focus.name} 直接关联的作品包括：{'、'.join(sorted(set(works)))}。"

        if any(keyword in lowered_question for keyword in ["谁作词", "词作者", "谁写词"]):
            lyricists = _related_labels(graph, focus.id, {"WROTE_LYRICS_FOR"}, {"Person"})
            if lyricists:
                return f"基于当前图谱，{focus.name} 的作词相关人物包括：{'、'.join(sorted(set(lyricists)))}。"

        if any(keyword in lowered_question for keyword in ["谁作曲", "作曲"]):
            composers = _related_labels(graph, focus.id, {"COMPOSED"}, {"Person"})
            if composers:
                return f"基于当前图谱，{focus.name} 的作曲相关人物包括：{'、'.join(sorted(set(composers)))}。"

        if any(keyword in lowered_question for keyword in ["谁唱", "谁演唱", "演唱"]):
            performers = _related_labels(graph, focus.id, {"PERFORMED"}, {"Person", "Band"})
            if performers:
                return f"基于当前图谱，{focus.name} 的演唱相关人物包括：{'、'.join(sorted(set(performers)))}。"

        related_facts = [_link_text(link, node_map) for link in focus_links[:4]]
        if related_facts:
            return (
                f"基于当前图谱，{focus.name} 是一个 {TYPE_LABELS.get(focus.type, focus.type)}。"
                f"当前可直接确认的关系包括：{'；'.join(related_facts)}。"
            )

        return (
            f"基于当前图谱，已检索到与问题最相关的实体是 {focus.name}。"
            f"现有证据主要来自它的节点属性与相邻关系，但可直接回答的信息仍然有限。"
        )
