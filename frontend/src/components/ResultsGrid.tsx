import { useAppSelector } from "../store/hooks";
import type { EntityType, GitHubRepository, GitHubUser, SearchItem } from "../types";
import RepoCard from "./RepoCard";
import UserCard from "./UserCard";
import SkeletonGrid from "./SkeletonGrid";

function isUser(item: SearchItem): item is GitHubUser {
  return "login" in item && !("full_name" in item);
}

function isRepo(item: SearchItem): item is GitHubRepository {
  return "full_name" in item;
}

interface ResultsGridProps {
  entityType: EntityType;
}

export default function ResultsGrid({ entityType }: ResultsGridProps) {
  const { items, status, totalCount, fromCache, error } = useAppSelector(
    (s) => s.search
  );

  if (status === "loading") {
    return <SkeletonGrid count={9} />;
  }

  if (status === "error" && error) {
    return (
      <div className="status-message status-message--error" role="alert">
        <div className="status-message__icon">⚠️</div>
        <div className="status-message__title">Something went wrong</div>
        <p className="status-message__subtitle">{error}</p>
      </div>
    );
  }

  if (status === "success" && items.length === 0) {
    return (
      <div className="status-message" role="status">
        <div className="status-message__icon">🔍</div>
        <div className="status-message__title">No results found</div>
        <p className="status-message__subtitle">
          Try a different search term or entity type.
        </p>
      </div>
    );
  }

  if (status !== "success" || items.length === 0) return null;

  return (
    <section className="results-section" aria-label="Search results">
      {/* Meta row */}
      <div className="results-meta">
        <p className="results-meta__count">
          Showing <strong>{items.length}</strong> of{" "}
          <strong>{totalCount.toLocaleString()}</strong>{" "}
          {entityType === "users" ? "users" : "repositories"}
        </p>
        {fromCache && (
          <span className="results-meta__cached" aria-label="Results loaded from cache">
            <svg
              width={10}
              height={10}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2.5}
              aria-hidden="true"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Cached
          </span>
        )}
      </div>

      {/* Grid */}
      <div className="results-grid">
        {items.map((item: SearchItem) => {
          if (entityType === "repositories" && isRepo(item)) {
            return <RepoCard key={item.id} repo={item} />;
          }
          if (entityType === "users" && isUser(item)) {
            return <UserCard key={item.id} user={item} />;
          }
          return null;
        })}
      </div>
    </section>
  );
}
