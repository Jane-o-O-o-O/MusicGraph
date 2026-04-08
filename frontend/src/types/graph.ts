export type EntityType = "Person" | "Band" | "Work" | "Album" | "Genre";

export interface SearchItem {
  id: string;
  name: string;
  type: string;
  summary?: string | null;
}

export interface EntityDetails {
  id: string;
  name: string;
  type: string;
  aliases: string[];
  summary?: string | null;
  meta: Record<string, unknown>;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  summary?: string | null;
  meta: Record<string, unknown>;
}

export interface GraphLink {
  id: string;
  source: string;
  target: string;
  type: string;
  meta: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface PathResponse extends GraphData {
  source_id: string;
  target_id: string;
}
