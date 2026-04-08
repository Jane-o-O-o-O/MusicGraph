import { startTransition, useDeferredValue, useEffect, useState } from "react";

import { fetchEntity, fetchGraph, fetchPath, searchEntities } from "./api/client";
import { DetailPanel } from "./components/DetailPanel";
import { GraphView } from "./components/GraphView";
import { SearchPanel } from "./components/SearchPanel";
import type { EntityDetails, GraphData, SearchItem } from "./types/graph";

const SAMPLE_ENTITIES: SearchItem[] = [
  {
    id: "person_jay_chou",
    name: "周杰伦",
    type: "Person",
    summary: "Singer, composer, and producer.",
  },
  {
    id: "person_fang_wenshan",
    name: "方文山",
    type: "Person",
    summary: "Lyricist and frequent collaborator.",
  },
  {
    id: "band_mayday",
    name: "五月天",
    type: "Band",
    summary: "Mandarin rock band.",
  },
  {
    id: "work_qinghuaci",
    name: "青花瓷",
    type: "Work",
    summary: "A representative Jay Chou work.",
  },
];

function mergeGraphData(currentGraph: GraphData, incomingGraph: GraphData): GraphData {
  const nodeMap = new Map(currentGraph.nodes.map((node) => [node.id, node]));
  const linkMap = new Map(currentGraph.links.map((link) => [link.id, link]));

  for (const node of incomingGraph.nodes) {
    nodeMap.set(node.id, node);
  }
  for (const link of incomingGraph.links) {
    linkMap.set(link.id, link);
  }

  return {
    nodes: [...nodeMap.values()],
    links: [...linkMap.values()],
  };
}

export default function App() {
  const [query, setQuery] = useState("");
  const [entityType, setEntityType] = useState("");
  const [results, setResults] = useState<SearchItem[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<EntityDetails | null>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [searchLoading, setSearchLoading] = useState(false);
  const [graphLoading, setGraphLoading] = useState(false);
  const [pathLoading, setPathLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pathFrom, setPathFrom] = useState("person_jay_chou");
  const [pathTo, setPathTo] = useState("person_fang_wenshan");
  const [expandedNodeIds, setExpandedNodeIds] = useState<string[]>([]);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [highlightedLinkIds, setHighlightedLinkIds] = useState<string[]>([]);

  const deferredGraphData = useDeferredValue(graphData);

  useEffect(() => {
    void loadEntityContext("person_jay_chou", true);
  }, []);

  async function loadEntityContext(entityId: string, replaceGraph: boolean) {
    setErrorMessage(null);
    setGraphLoading(true);
    try {
      const [entity, graph] = await Promise.all([fetchEntity(entityId), fetchGraph(entityId, 1)]);
      startTransition(() => {
        setSelectedEntity(entity);
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
    setPathFrom(item.id);
    await loadEntityContext(item.id, true);
  }

  async function handleNodeClick(nodeId: string) {
    setErrorMessage(null);
    try {
      const entity = await fetchEntity(nodeId);
      setSelectedEntity(entity);
      setHighlightedNodeIds([nodeId]);
      setPathFrom(nodeId);

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

  async function handleHighlightPath() {
    if (!pathFrom.trim() || !pathTo.trim()) {
      return;
    }

    setErrorMessage(null);
    setPathLoading(true);
    try {
      const pathGraph = await fetchPath(pathFrom.trim(), pathTo.trim());
      startTransition(() => {
        setHighlightedNodeIds(pathGraph.nodes.map((node) => node.id));
        setHighlightedLinkIds(pathGraph.links.map((link) => link.id));
        setGraphData((current) => mergeGraphData(current, pathGraph));
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to load path.");
    } finally {
      setPathLoading(false);
    }
  }

  const typeCounts: Record<string, number> = {};
  for (const node of graphData.nodes) {
    typeCounts[node.type] = (typeCounts[node.type] ?? 0) + 1;
  }

  return (
    <div className="app-shell">
      <div className="backdrop" />
      <SearchPanel
        query={query}
        entityType={entityType}
        pathFrom={pathFrom}
        pathTo={pathTo}
        loading={searchLoading}
        pathLoading={pathLoading}
        results={results}
        selectedEntityId={selectedEntity?.id ?? null}
        sampleItems={SAMPLE_ENTITIES}
        graphNodeCount={graphData.nodes.length}
        graphLinkCount={graphData.links.length}
        expandedCount={expandedNodeIds.length}
        onQueryChange={setQuery}
        onEntityTypeChange={setEntityType}
        onPathFromChange={setPathFrom}
        onPathToChange={setPathTo}
        onSearch={handleSearch}
        onSearchKeyDown={() => {
          void handleSearch();
        }}
        onSelect={(item) => {
          void handleSelect(item);
        }}
        onHighlightPath={() => {
          void handleHighlightPath();
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
          typeCounts={typeCounts}
          onNodeClick={(node) => {
            void handleNodeClick(node.id);
          }}
        />
      </main>

      <DetailPanel entity={selectedEntity} errorMessage={errorMessage} />
    </div>
  );
}
