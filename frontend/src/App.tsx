import { startTransition, useDeferredValue, useEffect, useState } from "react";

import { fetchEntity, fetchGraph, queryGraphRag, searchEntities } from "./api/client";
import { DetailPanel } from "./components/DetailPanel";
import { GraphRagDock } from "./components/GraphRagDock";
import { GraphView } from "./components/GraphView";
import { SearchPanel } from "./components/SearchPanel";
import type {
  EntityDetails,
  GraphData,
  GraphLink,
  GraphRagResponse,
  SearchItem,
} from "./types/graph";

const SAMPLE_ENTITIES: SearchItem[] = [
  {
    id: "person_jay_chou",
    name: "\u5468\u6770\u4f26",
    type: "Person",
    summary: "Singer, composer, and producer.",
  },
  {
    id: "person_fang_wenshan",
    name: "\u65b9\u6587\u5c71",
    type: "Person",
    summary: "Lyricist and frequent collaborator.",
  },
  {
    id: "person_jolin_tsai",
    name: "\u8521\u4f9d\u6797",
    type: "Person",
    summary: "Pop singer with crossover collaborations.",
  },
  {
    id: "band_mayday",
    name: "\u4e94\u6708\u5929",
    type: "Band",
    summary: "Mandarin rock band.",
  },
  {
    id: "work_qinghuaci",
    name: "\u9752\u82b1\u74f7",
    type: "Work",
    summary: "A representative Jay Chou work.",
  },
  {
    id: "work_turanhaoxiangni",
    name: "\u7a81\u7136\u597d\u60f3\u4f60",
    type: "Work",
    summary: "A signature Mayday stadium ballad.",
  },
];

function getLinkEndpointId(endpoint: GraphLink["source"] | { id?: unknown }): string | null {
  if (typeof endpoint === "string") {
    return endpoint;
  }
  if (
    endpoint &&
    typeof endpoint === "object" &&
    "id" in endpoint &&
    typeof endpoint.id === "string"
  ) {
    return endpoint.id;
  }
  return null;
}

function normalizeGraphData(graph: GraphData): GraphData {
  const nodeMap = new Map(
    graph.nodes.map((node) => [
      node.id,
      {
        ...node,
        meta: { ...node.meta },
      },
    ]),
  );
  const linkMap = new Map<string, GraphLink>();

  for (const link of graph.links) {
    const sourceId = getLinkEndpointId(link.source);
    const targetId = getLinkEndpointId(link.target);
    if (!sourceId || !targetId || !nodeMap.has(sourceId) || !nodeMap.has(targetId)) {
      continue;
    }

    linkMap.set(link.id, {
      ...link,
      source: sourceId,
      target: targetId,
      meta: { ...link.meta },
    });
  }

  return {
    nodes: [...nodeMap.values()],
    links: [...linkMap.values()],
  };
}

function mergeGraphData(currentGraph: GraphData, incomingGraph: GraphData): GraphData {
  const nodeMap = new Map(currentGraph.nodes.map((node) => [node.id, node]));

  for (const node of incomingGraph.nodes) {
    nodeMap.set(node.id, node);
  }

  return normalizeGraphData({
    nodes: [...nodeMap.values()],
    links: [...currentGraph.links, ...incomingGraph.links],
  });
}

export default function App() {
  const [query, setQuery] = useState("");
  const [entityType, setEntityType] = useState("");
  const [results, setResults] = useState<SearchItem[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<EntityDetails | null>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [searchLoading, setSearchLoading] = useState(false);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphRagLoading, setGraphRagLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [graphRagQuestion, setGraphRagQuestion] = useState("");
  const [graphRagResult, setGraphRagResult] = useState<GraphRagResponse | null>(null);
  const [expandedNodeIds, setExpandedNodeIds] = useState<string[]>([]);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [highlightedLinkIds, setHighlightedLinkIds] = useState<string[]>([]);
  const [detailVisible, setDetailVisible] = useState(false);

  const deferredGraphData = useDeferredValue(graphData);

  useEffect(() => {
    void loadEntityContext("person_jay_chou", true, false);
  }, []);

  async function loadEntityContext(entityId: string, replaceGraph: boolean, showDetail: boolean) {
    setErrorMessage(null);
    setGraphLoading(true);
    try {
      const [entity, graph] = await Promise.all([fetchEntity(entityId), fetchGraph(entityId, 1)]);
      startTransition(() => {
        setSelectedEntity(showDetail ? entity : null);
        setDetailVisible(showDetail);
        setHighlightedNodeIds([entityId]);
        setHighlightedLinkIds([]);
        setExpandedNodeIds((current) =>
          replaceGraph ? [entityId] : Array.from(new Set([...current, entityId])),
        );
        setGraphData((current) => (replaceGraph ? graph : mergeGraphData(current, graph)));
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to load entity.");
    } finally {
      setGraphLoading(false);
    }
  }

  async function handleSearch() {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setErrorMessage(null);
    setSearchLoading(true);
    try {
      const items = await searchEntities(query, entityType);
      startTransition(() => {
        setResults(items);
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Search failed.");
    } finally {
      setSearchLoading(false);
    }
  }

  async function handleSelect(item: SearchItem) {
    await loadEntityContext(item.id, true, true);
  }

  async function handleNodeClick(nodeId: string) {
    setErrorMessage(null);
    try {
      const entity = await fetchEntity(nodeId);
      setSelectedEntity(entity);
      setDetailVisible(true);
      setHighlightedNodeIds([nodeId]);

      if (!expandedNodeIds.includes(nodeId)) {
        setGraphLoading(true);
        const graph = await fetchGraph(nodeId, 1);
        startTransition(() => {
          setExpandedNodeIds((current) => Array.from(new Set([...current, nodeId])));
          setGraphData((current) => mergeGraphData(current, graph));
        });
        setGraphLoading(false);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to expand node.");
      setGraphLoading(false);
    }
  }

  async function handleGraphRagQuery() {
    if (!graphRagQuestion.trim()) {
      return;
    }

    setErrorMessage(null);
    setGraphRagLoading(true);
    try {
      const entityIds = selectedEntity ? [selectedEntity.id] : [];
      const response = await queryGraphRag(graphRagQuestion.trim(), entityIds);
      startTransition(() => {
        setGraphRagResult(response);
        setHighlightedNodeIds(response.matched_entities.map((item) => item.id));
        setHighlightedLinkIds(response.graph.links.map((link) => link.id));
        setExpandedNodeIds((current) =>
          Array.from(
            new Set([
              ...current,
              ...response.matched_entities.map((item) => item.id),
            ]),
          ),
        );
        setGraphData((current) => mergeGraphData(current, response.graph));
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "GraphRAG query failed.");
    } finally {
      setGraphRagLoading(false);
    }
  }

  return (
    <div className={`app-shell ${detailVisible ? "detail-open" : ""}`}>
      <div className="backdrop" />
      <SearchPanel
        query={query}
        entityType={entityType}
        loading={searchLoading}
        results={results}
        selectedEntityId={selectedEntity?.id ?? null}
        sampleItems={SAMPLE_ENTITIES}
        graphNodeCount={graphData.nodes.length}
        graphLinkCount={graphData.links.length}
        expandedCount={expandedNodeIds.length}
        onQueryChange={setQuery}
        onEntityTypeChange={setEntityType}
        onSearch={handleSearch}
        onSearchKeyDown={() => {
          void handleSearch();
        }}
        onSelect={(item) => {
          void handleSelect(item);
        }}
      />

      <main className="graph-panel">
        <GraphView
          graphData={deferredGraphData}
          loading={graphLoading}
          highlightedNodeIds={highlightedNodeIds}
          highlightedLinkIds={highlightedLinkIds}
          selectedEntityId={selectedEntity?.id ?? null}
          expandedCount={expandedNodeIds.length}
          onNodeClick={(node) => {
            void handleNodeClick(node.id);
          }}
        />
      </main>

      <GraphRagDock
        question={graphRagQuestion}
        loading={graphRagLoading}
        result={graphRagResult}
        selectedEntityId={selectedEntity?.id ?? null}
        onQuestionChange={setGraphRagQuestion}
        onSubmit={() => {
          void handleGraphRagQuery();
        }}
      />

      <DetailPanel entity={selectedEntity} errorMessage={errorMessage} visible={detailVisible} />
    </div>
  );
}
