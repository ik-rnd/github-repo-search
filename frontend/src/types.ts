/**
 * Type definitions shared across the frontend.
 */

export type GitProvider = "github" | "gitlab" | "codeberg";

export type EntityType = "users" | "repositories";

export type SearchStatus = "idle" | "loading" | "success" | "error";

// ---- GitHub API response shapes ----

export interface GitHubOwner {
  login: string;
  avatar_url: string;
  html_url: string;
}

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
  watchers_count: number;
  language: string | null;
  owner: GitHubOwner;
  updated_at: string;
  topics: string[];
}

export interface GitHubUser {
  id: number;
  login: string;
  avatar_url: string;
  html_url: string;
  type: string;
  score: number;
}

export type SearchItem = GitHubRepository | GitHubUser;

export interface SearchResponse {
  total_count: number;
  entity_type: EntityType;
  items: SearchItem[];
  cached: boolean;
}

// ---- Redux store ----

export interface CachedResult {
  total_count: number;
  items: SearchItem[];
  cached: boolean;
}

export interface SearchState {
  query: string;
  provider: GitProvider;
  entityType: EntityType;
  status: SearchStatus;
  error: string | null;
  totalCount: number;
  items: SearchItem[];
  /** In-memory cache keyed by "query:entityType" */
  cache: Record<string, CachedResult>;
  fromCache: boolean;
}
