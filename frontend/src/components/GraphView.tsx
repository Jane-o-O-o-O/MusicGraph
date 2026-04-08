import { useEffect, useRef } from "react";
import ForceGraph3D from "react-force-graph-3d";

import type { GraphData, GraphLink, GraphNode } from "../types/graph";

interface GraphViewProps {
  graphData: GraphData;
  loading: boolean;
  highlightedNodeIds: string[];
  highlightedLinkIds: string[];
  onNodeClick: (node: GraphNode) => void;
}

export function GraphView(props: GraphViewProps) {
  const { graphData, loading, highlightedNodeIds, highlightedLinkIds, onNodeClick } = props;
  const graphRef = useRef<any>(null);

  useEffect(() => {
    if (!graphRef.current || graphData.nodes.length === 0) {
      return;
    }
    graphRef.current.zoomToFit(500, 80);
  }, [graphData]);

  const highlightedNodeSet = new Set(highlightedNodeIds);
  const highlightedLinkSet = new Set(highlightedLinkIds);

  if (graphData.nodes.length === 0) {
    return (
      <div className="graph-empty">
        <h2>3D graph waiting for data</h2>
        <p>Search an entity or use the sample IDs to load the first subgraph.</p>
      </div>
    );
  }

  return (
    <div className="graph-stage">
      <div className="graph-status">
        <span>{loading ? "Refreshing graph..." : "3D view ready"}</span>
        <span>{graphData.nodes.length} nodes</span>
        <span>{graphData.links.length} links</span>
      </div>
      <ForceGraph3D
        ref={graphRef}
        graphData={graphData}
        backgroundColor="#08141e"
        nodeAutoColorBy="type"
        nodeLabel={(node: object) => {
          const graphNode = node as GraphNode;
          return `${graphNode.label} (${graphNode.type})`;
        }}
        nodeVal={(node: object) => {
          const graphNode = node as GraphNode;
          return highlightedNodeSet.has(graphNode.id) ? 10 : 6;
        }}
        nodeColor={(node: object) => {
          const graphNode = node as GraphNode;
          if (highlightedNodeSet.has(graphNode.id)) {
            return "#fbbf24";
          }
          return undefined;
        }}
        linkLabel={(link: object) => {
          const graphLink = link as GraphLink;
          return graphLink.type;
        }}
        linkWidth={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? 4 : 1.5;
        }}
        linkColor={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? "#f97316" : "#78b7ff";
        }}
        onNodeClick={(node: object) => onNodeClick(node as GraphNode)}
      />
    </div>
  );
}
