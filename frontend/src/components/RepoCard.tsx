import { useState } from "react";
import type { GitHubRepository } from "../types";
import { useAppSelector } from "../store/hooks";

// Language colour map (subset of GitHub's language colours)
const LANG_COLORS: Record<string, string> = {
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Python: "#3572A5",
  Go: "#00ADD8",
  Rust: "#dea584",
  Java: "#b07219",
  "C++": "#f34b7d",
  C: "#555555",
  "C#": "#178600",
  Ruby: "#701516",
  PHP: "#4F5D95",
  Swift: "#F05138",
  Kotlin: "#A97BFF",
  Dart: "#00B4AB",
  Scala: "#c22d40",
  Shell: "#89e051",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Vue: "#41b883",
  Svelte: "#ff3e00",
};

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const days = Math.floor(diff / 86_400_000);
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;
  return `${Math.floor(months / 12)}y ago`;
}

interface RepoCardProps {
  repo: GitHubRepository;
}

export default function RepoCard({ repo }: RepoCardProps) {
  const langColor = repo.language ? (LANG_COLORS[repo.language] ?? "#8b949e") : null;
  const provider = useAppSelector((s) => s.search.provider);
  const authTokens = useAppSelector((s) => (s as any).auth?.tokens || {});

  const [isStarring, setIsStarring] = useState(false);
  const [isForking, setIsForking] = useState(false);

  const handleAction = async (action: "star" | "fork") => {
    const token = authTokens[provider];
    if (!token) {
      alert(`Please login to ${provider} to ${action} this repository.`);
      return;
    }

    if (action === "star") setIsStarring(true);
    if (action === "fork") setIsForking(true);

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
      const res = await fetch(`${baseUrl}/api/repos/${action}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ repo_full_name: repo.full_name })
      });

      const data = await res.json();
      if (res.ok) {
        alert(`${action === "star" ? "Starred" : "Forked"} successfully!`);
      } else {
        alert(data.error || `Failed to ${action}.`);
      }
    } catch (e) {
      alert(`Network error during ${action}.`);
    } finally {
      if (action === "star") setIsStarring(false);
      if (action === "fork") setIsForking(false);
    }
  };

  return (
    <article className="repo-card" aria-label={`Repository: ${repo.full_name}`}>
      {/* Header — owner avatar + name */}
      <div className="repo-card__header">
        <img
          src={repo.owner.avatar_url}
          alt={`${repo.owner.login}'s avatar`}
          className="repo-card__avatar"
          loading="lazy"
        />
        <div style={{ overflow: "hidden" }}>
          <div className="repo-card__owner-name">{repo.owner.login}</div>
          <a
            className="repo-card__name"
            href={repo.html_url}
            target="_blank"
            rel="noopener noreferrer"
            title={repo.full_name}
          >
            {repo.name}
          </a>
        </div>
      </div>

      {/* Description */}
      {repo.description && (
        <p className="repo-card__description">{repo.description}</p>
      )}

      {/* Topics */}
      {repo.topics && repo.topics.length > 0 && (
        <div className="repo-card__topics" aria-label="Topics">
          {repo.topics.slice(0, 4).map((topic) => (
            <span key={topic} className="repo-card__topic">
              {topic}
            </span>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="repo-card__stats">
        {/* Language */}
        {repo.language && (
          <span className="repo-card__stat" aria-label={`Language: ${repo.language}`}>
            <span
              className="repo-card__lang-dot"
              style={{ background: langColor ?? undefined }}
            />
            {repo.language}
          </span>
        )}

        {/* Stars */}
        <button
          onClick={() => handleAction("star")}
          disabled={isStarring}
          className="repo-card__stat repo-card__stat--link disabled:opacity-50"
          aria-label={`${repo.stargazers_count} stars`}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
          {isStarring ? "..." : formatNumber(repo.stargazers_count)}
        </button>

        {/* Forks */}
        <button
          onClick={() => handleAction("fork")}
          disabled={isForking}
          className="repo-card__stat repo-card__stat--link disabled:opacity-50"
          aria-label={`${repo.forks_count} forks`}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
            <line x1={6} y1={3} x2={6} y2={15} />
            <circle cx={18} cy={6} r={3} />
            <circle cx={6} cy={18} r={3} />
            <circle cx={6} cy={6} r={3} />
            <path d="M18 9a9 9 0 0 1-9 9" />
          </svg>
          {isForking ? "..." : formatNumber(repo.forks_count)}
        </button>

        {/* Updated */}
        <span className="repo-card__stat" aria-label={`Updated ${timeAgo(repo.updated_at)}`}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
            <circle cx={12} cy={12} r={10} />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          {timeAgo(repo.updated_at)}
        </span>
      </div>
    </article>
  );
}
