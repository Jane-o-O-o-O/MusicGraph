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
  onNodeClick: (node: GraphNode) => void;
}

const NODE_COLORS: Record<string, string> = {
  Person: "#6fd3ff",
  Location: "#8fd18a",
  Event: "#ff9b8f",
  Title: "#d5b3ff",
  Band: "#ffb56b",
  Work: "#7df0c4",
  Album: "#ffe08b",
  Genre: "#ff8f8f",
};

const RELATIONSHIP_LABELS: Record<string, string> = {
  ASSOCIATED_WITH: "关联",
  LOCATED_AT: "位于",
  OCCURRED_IN: "发生于",
  HELD_TITLE: "官职",
  PARTICIPATED_IN: "参与",
  ALLIED_WITH: "结盟",
  FOUGHT_AGAINST: "交战",
  SWORN_BROTHERS: "结义",
  SERVED_UNDER: "效力于",
  PERFORMED: "演唱",
  COMPOSED: "创作",
  WROTE_LYRICS_FOR: "作词",
  IN_ALBUM: "收录于",
  HAS_GENRE: "风格",
  MEMBER_OF: "成员",
};

function getNodeRadius(
  node: GraphNode,
  highlightedNodeSet: Set<string>,
  selectedEntityId: string | null,
): number {
  if (highlightedNodeSet.has(node.id)) {
    return 8.5;
  }
  if (selectedEntityId === node.id) {
    return 7.25;
  }
  return 4.2;
}

function createTextTexture(
  text: string,
  color: string,
  fontSize: number,
  strokeWidth: number,
): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  if (!context) {
    return new THREE.CanvasTexture(canvas);
  }

  context.font = `700 ${fontSize}px Bahnschrift, "Segoe UI", sans-serif`;
  const textWidth = context.measureText(text).width;
  canvas.width = Math.ceil(textWidth + 24);
  canvas.height = fontSize + 18;

  const drawContext = canvas.getContext("2d");
  if (!drawContext) {
    return new THREE.CanvasTexture(canvas);
  }

  drawContext.font = `700 ${fontSize}px Bahnschrift, "Segoe UI", sans-serif`;
  drawContext.textAlign = "center";
  drawContext.textBaseline = "middle";
  drawContext.lineWidth = strokeWidth;
  drawContext.strokeStyle = "rgba(6, 13, 20, 0.9)";
  drawContext.fillStyle = color;
  drawContext.strokeText(text, canvas.width / 2, canvas.height / 2);
  drawContext.fillText(text, canvas.width / 2, canvas.height / 2);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

export function GraphView(props: GraphViewProps) {
  const {
    graphData,
    loading,
    highlightedNodeIds,
    highlightedLinkIds,
    selectedEntityId,
    expandedCount,
    onNodeClick,
  } = props;

  const graphRef = useRef<any>(null);
  const labelTextureCache = useRef(new Map<string, THREE.CanvasTexture>());
  const linkLabelMaterialCache = useRef(new Map<string, THREE.SpriteMaterial>());
  const linkMaterialCache = useRef(
    new Map<string, THREE.MeshBasicMaterial | THREE.LineBasicMaterial>(),
  );

  useEffect(() => {
    return () => {
      for (const texture of labelTextureCache.current.values()) {
        texture.dispose();
      }
      labelTextureCache.current.clear();

      for (const material of linkMaterialCache.current.values()) {
        material.dispose();
      }
      linkMaterialCache.current.clear();

      for (const material of linkLabelMaterialCache.current.values()) {
        material.map?.dispose();
        material.dispose();
      }
      linkLabelMaterialCache.current.clear();
    };
  }, []);

  useEffect(() => {
    if (!graphRef.current || graphData.nodes.length === 0) {
      return;
    }

    graphRef.current.d3Force("charge")?.strength(-220);
    graphRef.current.d3VelocityDecay?.(0.34);
    graphRef.current.zoomToFit(500, 100);
  }, [graphData]);

  const highlightedNodeSet = new Set(highlightedNodeIds);
  const highlightedLinkSet = new Set(highlightedLinkIds);

  function getLinkMaterial(link: GraphLink): THREE.MeshBasicMaterial | THREE.LineBasicMaterial {
    const isHighlighted = highlightedLinkSet.has(link.id);
    const cacheKey = isHighlighted ? "highlight" : "normal";
    const cached = linkMaterialCache.current.get(cacheKey);
    if (cached) {
      return cached;
    }

    const material =
      linkWidth(link) > 0
        ? new THREE.MeshBasicMaterial({
            color: isHighlighted ? "#ffd38a" : "#74c7ff",
            transparent: true,
            opacity: isHighlighted ? 0.92 : 0.18,
          })
        : new THREE.LineBasicMaterial({
            color: isHighlighted ? "#ffd38a" : "#74c7ff",
            transparent: true,
            opacity: isHighlighted ? 0.92 : 0.18,
          });

    linkMaterialCache.current.set(cacheKey, material);
    return material;
  }

  function formatRelationshipLabel(type: string): string {
    return RELATIONSHIP_LABELS[type] ?? type.replaceAll("_", " ");
  }

  function getLinkLabelMaterial(link: GraphLink): THREE.SpriteMaterial {
    const isHighlighted = highlightedLinkSet.has(link.id);
    const relationLabel = formatRelationshipLabel(link.type);
    const cacheKey = `${relationLabel}:${isHighlighted ? "highlight" : "normal"}`;
    const cached = linkLabelMaterialCache.current.get(cacheKey);
    if (cached) {
      return cached;
    }

    const texture = createTextTexture(
      relationLabel,
      isHighlighted ? "#ffe0a3" : "#8fb2cc",
      isHighlighted ? 26 : 22,
      isHighlighted ? 6 : 5,
    );
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthWrite: false,
      depthTest: false,
      opacity: isHighlighted ? 0.95 : 0.68,
    });
    linkLabelMaterialCache.current.set(cacheKey, material);
    return material;
  }

  function createLinkLabelObject(link: GraphLink): THREE.Sprite {
    const material = getLinkLabelMaterial(link);
    const sprite = new THREE.Sprite(material);
    const texture = material.map;
    const height = highlightedLinkSet.has(link.id) ? 4.2 : 3.4;
    const image = texture?.image as { width?: number; height?: number } | undefined;
    const widthRatio =
      image && image.width && image.height ? image.width / image.height : 2.4;
    sprite.scale.set(height * widthRatio, height, 1);
    sprite.renderOrder = 12;
    return sprite;
  }

  function createNodeObject(node: GraphNode): THREE.Object3D {
    const isHighlighted = highlightedNodeSet.has(node.id);
    const isSelected = selectedEntityId === node.id;
    const radius = getNodeRadius(node, highlightedNodeSet, selectedEntityId);
    const color = NODE_COLORS[node.type] ?? "#d7e5f4";

    const group = new THREE.Group();

    const haloMaterial = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: isHighlighted ? 0.22 : isSelected ? 0.16 : 0.08,
      depthWrite: false,
    });
    const halo = new THREE.Mesh(
      new THREE.SphereGeometry(radius * (isHighlighted ? 2.2 : 1.95), 20, 20),
      haloMaterial,
    );
    group.add(halo);

    const coreMaterial = new THREE.MeshPhongMaterial({
      color,
      emissive: new THREE.Color(color).multiplyScalar(isHighlighted ? 0.5 : 0.28),
      shininess: 90,
      transparent: true,
      opacity: isHighlighted ? 1 : 0.96,
    });
    const core = new THREE.Mesh(new THREE.SphereGeometry(radius, 24, 24), coreMaterial);
    group.add(core);

    const fontSize = isHighlighted ? 34 : isSelected ? 28 : 22;
    const strokeWidth = isHighlighted ? 8 : isSelected ? 6 : 5;
    const textureKey = `${node.id}:${node.label}:${isHighlighted ? "1" : "0"}:${isSelected ? "1" : "0"}`;
    let texture = labelTextureCache.current.get(textureKey);
    if (!texture) {
      texture = createTextTexture(
        node.label,
        isHighlighted ? "#fff0c3" : isSelected ? "#eef7ff" : "#a9bfd3",
        fontSize,
        strokeWidth,
      );
      labelTextureCache.current.set(textureKey, texture);
    }

    const label = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
        depthTest: false,
        opacity: isHighlighted ? 1 : isSelected ? 0.96 : 0.72,
      }),
    );
    const height = isHighlighted ? 7.2 : isSelected ? 6.2 : 4.9;
    const width = height * (texture.image.width / texture.image.height);
    label.scale.set(width, height, 1);
    label.center.set(0.5, 0);
    label.position.set(0, radius + 1.45, 0);
    label.renderOrder = 10;
    group.add(label);

    return group;
  }

  function linkWidth(link: GraphLink): number {
    return highlightedLinkSet.has(link.id) ? 2.4 : 0;
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="graph-empty">
        <h2>等待首个 3D 子图</h2>
        <p>从左侧快速开始，或者直接搜索实体后把它加载进图谱舞台。</p>
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
        <p>亮色只保留给焦点和命中关系，其余节点与连线退后，画面会干净很多。</p>
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
          return getNodeRadius(graphNode, highlightedNodeSet, selectedEntityId);
        }}
        nodeThreeObject={(node: object) => createNodeObject(node as GraphNode)}
        nodeColor={() => "#000000"}
        nodeOpacity={0}
        linkLabel={(link: object) => {
          const graphLink = link as GraphLink;
          return formatRelationshipLabel(graphLink.type);
        }}
        linkThreeObjectExtend
        linkThreeObject={(link: object) => createLinkLabelObject(link as GraphLink)}
        linkPositionUpdate={(spriteObject: object, coords: object) => {
          const sprite = spriteObject as THREE.Object3D;
          const position = coords as {
            start: { x: number; y: number; z: number };
            end: { x: number; y: number; z: number };
          };
          const midX = (position.start.x + position.end.x) / 2;
          const midY = (position.start.y + position.end.y) / 2;
          const midZ = (position.start.z + position.end.z) / 2;
          sprite.position.set(midX, midY, midZ);
          return true;
        }}
        linkColor={(link: object) => {
          const graphLink = link as GraphLink;
          return highlightedLinkSet.has(graphLink.id) ? "#ffd38a" : "rgba(116, 199, 255, 0.16)";
        }}
        linkMaterial={(link: object) => getLinkMaterial(link as GraphLink)}
        linkWidth={(link: object) => linkWidth(link as GraphLink)}
        linkOpacity={1}
        linkCurvature={0.04}
        linkDirectionalParticles={0}
        linkDirectionalArrowLength={0}
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
