import axios from "axios";
import type { EntityType, SearchResponse } from "../types";

const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15_000,
});

export async function searchGitHub(
  query: string,
  entityType: EntityType
): Promise<SearchResponse> {
  const response = await apiClient.post<SearchResponse>("/search/", {
    query,
    entity_type: entityType,
  });
  return response.data;
}

export async function clearCache(): Promise<void> {
  await apiClient.post("/clear-cache/");
}
