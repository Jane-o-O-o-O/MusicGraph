import { useEffect, useRef } from "react";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from "three";

import type { GraphData, GraphLink, GraphNode } from "../types/graph";

interface GraphViewProps {
  graphData: GraphData;
  loading: boolean;
  highlightedNodeIds: string[];
  highlightedLinkIds: string[];
  selectedEntityId: string | null;
  expandedCount: number;
  typeCounts: Record<string, number>;
  onNodeClick: (node: GraphNode) => void;
}

const NODE_COLORS: Record<string, string> = {
  Person: "#53c7ff",
  Band: "#ff9d4d",
  Work: "#4ce1a2",
  Album: "#f4d06f",
  Genre: "#ff6b6b",
};

const LEGEND_ITEMS = [
  { key: "Person", label: "人物" },
  { key: "Band", label: "乐团" },
  { key: "Work", label: "作品" },
  { key: "Album", label: "专辑" },
  { key: "Genre", label: "流派" },
];

function getNodeSize(
  node: GraphNode,
  highlightedNodeSet: Set<string>,
  selectedEntityId: string | null,
): number {
  if (highlightedNodeSet.has(node.id)) {
    return 13;
  }
  if (selectedEntityId === node.id) {
    return 10;
  }
  return 6;
}

export function GraphView(props: GraphViewProps) {
  const {
    graphData,
    loading,
    highlightedNodeIds,
    highlightedLinkIds,
    selectedEntityId,
    expandedCount,
    typeCounts,
    onNodeClick,
  } = props;
  const graphRef = useRef<any>(null);
  const labelTextureCache = useRef(new Map<string, THREE.CanvasTexture>());

  useEffect(() => {
    return () => {
      for (const texture of labelTextureCache.current.values()) {
        texture.dispose();
      }
      labelTextureCache.current.clear();
    };
  }, []);

  useEffect(() => {
    if (!graphRef.current || graphData.nodes.length === 0) {
      return;
    }

    graphRef.current.d3Force("charge")?.strength(-260);
    graphRef.current.d3VelocityDecay?.(0.28);
    graphRef.current.zoomToFit(500, 90);
  }, [graphData]);

  const highlightedNodeSet = new Set(highlightedNodeIds);
  const highlightedLinkSet = new Set(highlightedLinkIds);

  function createLabelSprite(node: GraphNode): THREE.Sprite {
    const isHighlighted = highlightedNodeSet.has(node.id);
    const isSelected = selectedEntityId === node.id;
    const radius = getNodeSize(node, highlightedNodeSet, selectedEntityId);
    const fontSize = isHighlighted ? 44 : isSelected ? 40 : 32;
    const cacheKey = `${node.id}:${node.label}:${isHighlighted ? "1" : "0"}:${isSelected ? "1" : "0"}`;

    let texture = labelTextureCache.current.get(cacheKey);
    if (!texture) {
      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      if (!context) {
        return new THREE.Sprite();
      }

      context.font = `700 ${fontSize}px Bahnschrift, "Segoe UI", sans-serif`;
      const textWidth = context.measureText(node.label).width;
      canvas.width = Math.ceil(textWidth + 18);
      canvas.height = fontSize + 12;

      const drawContext = canvas.getContext("2d");
      if (!drawContext) {
        return new THREE.Sprite();
      }

      drawContext.font = `700 ${fontSize}px Bahnschrift, "Segoe UI", sans-serif`;
      drawContext.textAlign = "center";
      drawContext.textBaseline = "middle";
      drawContext.lineWidth = isHighlighted ? 8 : 6;
      drawContext.strokeStyle = "rgba(5, 12, 18, 0.88)";
      drawContext.fillStyle = isHighlighted
        ? "#ffe29a"
        : isSelected
          ? "#f4fbff"
          : "#dbeaf7";
      drawContext.strokeText(node.label, canvas.width / 2, canvas.height / 2);
      drawContext.fillText(node.label, canvas.width / 2, canvas.height / 2);

      texture = new THREE.CanvasTexture(canvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      labelTextureCache.current.set(cacheKey, texture);
    }

    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
        depthTest: false,
      }),
    );
    const height = isHighlighted ? 12 : isSelected ? 10.5 : 9;
    const width = height * (texture.image.width / texture.image.height);
    sprite.scale.set(width, height, 1);
    sprite.center.set(0.5, 0);
    sprite.position.set(0, radius + 2.4, 0);
    sprite.renderOrder = 10;
    return sprite;
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="graph-empty">
        <h2>等待首个 3D 子图</h2>
        <p>从左侧快速开始，或直接搜索实体后把它加载进图谱舞台。</p>
      </div>
    );
  }

  return (
    <div className="graph-stage">
      <div className="graph-status">
        <span>{loading ? "正在刷新图谱" : "3D 视图已就绪"}</span>
        <span>{graphData.nodes.length} 个节点</span>
        <span>{graphData.links.length} 条关系</span>
        <span>{expandedCount} 个已展开中心</span>
      </div>

      <div className="graph-overlay graph-overlay-top-right">
        <div className="graph-overlay-title">当前焦点</div>
        <strong>{selectedEntityId ?? "尚未选择"}</strong>
        <p>单击节点聚焦相机并继续展开，拖拽可旋转，滚轮可缩放。</p>
      </div>

      <div className="graph-overlay graph-overlay-bottom-left graph-legend">
        <div className="graph-overlay-title">图例</div>
        <div className="legend-list">
          {LEGEND_ITEMS.map((item) => (
            <div className="legend-item" key={item.key}>
              <span
                className="legend-dot"
                style={{ backgroundColor: NODE_COLORS[item.key] ?? "#d7e5f4" }}
              />
              <strong>{item.label}</strong>
              <small>{typeCounts[item.key] ?? 0}</small>
            </div>
          ))}
        </div>
      </div>

      <ForceGraph3D
        ref={graphRef}
        graphData={graphData}
        backgroundColor="#071018"
        showNavInfo={false}
        nodeLabel={(node: object) => {
          const graphNode = node as GraphNode;
          return `${graphNode.label} (${graphNode.type})`;
        }}
        nodeVal={(node: object) => {
          const graphNode = node as GraphNode;
          return getNodeSize(graphNode, highlightedNodeSet, selectedEntityId);
        }}
        nodeThreeObject={(node: object) => createLabelSprite(node as GraphNode)}
        nodeThreeObjectExtend
        nodeColor={(node: object) => {
          const graphNode = node as GraphNode;
          if (highlightedNodeSet.has(graphNode.id)) {
            return "#ffd166";
          }
          return NODE_COLORS[graphNode.type] ?? "#d7e5f4";
        }}
        nodeOpacity={0.95}
        linkLabel={(link: object) => {
          const graphLink = link as GraphLink;
          return graphLink.type;
        }}
        linkColor={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? "#ff8a3d" : "rgba(120, 183, 255, 0.44)";
        }}
        linkWidth={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? 4.6 : 1.4;
        }}
        linkOpacity={0.8}
        linkCurvature={0.08}
        linkDirectionalParticles={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? 4 : 0;
        }}
        linkDirectionalParticleWidth={3.2}
        linkDirectionalParticleSpeed={0.006}
        linkDirectionalArrowLength={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? 4 : 0;
        }}
        linkDirectionalArrowColor={() => "#ffd166"}
        cooldownTicks={90}
        warmupTicks={60}
        onNodeClick={(node: object) => {
          const graphNode = node as GraphNode & { x?: number; y?: number; z?: number };
          const distance = 110;
          const length = Math.hypot(graphNode.x ?? 0, graphNode.y ?? 0, graphNode.z ?? 0);
          if (graphRef.current && length > 0) {
            const distRatio = 1 + distance / length;
            graphRef.current.cameraPosition(
              {
                x: (graphNode.x ?? 0) * distRatio,
                y: (graphNode.y ?? 0) * distRatio,
                z: (graphNode.z ?? 0) * distRatio,
              },
              graphNode,
              850,
            );
          }
          onNodeClick(graphNode);
        }}
      />
    </div>
  );
}
