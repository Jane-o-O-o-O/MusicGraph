import type {
  EntityDetails,
  GraphData,
  GraphRagResponse,
  HealthResponse,
  SearchItem,
} from "../types/graph";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.toString() ?? "http://localhost:8000/api";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const fallback = `${response.status} ${response.statusText}`.trim();
    throw new Error(fallback || "Request failed.");
  }
  return (await response.json()) as T;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const fallback = `${response.status} ${response.statusText}`.trim();
    throw new Error(fallback || "Request failed.");
  }
  return (await response.json()) as T;
}

export async function searchEntities(
  query: string,
  entityType: string,
  limit = 20,
): Promise<SearchItem[]> {
  const params = new URLSearchParams();
  params.set("q", query);
  params.set("limit", String(limit));
  if (entityType) {
    params.set("type", entityType);
  }
  const response = await fetchJson<{ items: SearchItem[] }>(`/search?${params.toString()}`);
  return response.items;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>("/health");
}

export async function fetchEntity(entityId: string): Promise<EntityDetails> {
  return fetchJson<EntityDetails>(`/entities/${entityId}`);
}

export async function fetchGraph(entityId: string, depth = 1): Promise<GraphData> {
  return fetchJson<GraphData>(`/graph/${entityId}?depth=${depth}`);
}

export async function queryGraphRag(
  question: string,
  entityIds: string[] = [],
): Promise<GraphRagResponse> {
  return postJson<GraphRagResponse>("/graphrag/query", {
    question,
    entity_ids: entityIds,
    depth: 2,
    max_entities: 5,
  });
}
