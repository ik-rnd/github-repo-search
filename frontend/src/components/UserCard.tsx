import type { GitHubUser } from "../types";

interface UserCardProps {
  user: GitHubUser;
}

export default function UserCard({ user }: UserCardProps) {
  return (
    <article className="user-card" aria-label={`User: ${user.login}`}>
      <div className="user-card__avatar-wrapper">
        <img
          src={user.avatar_url}
          alt={`${user.login}'s avatar`}
          className="user-card__avatar"
          loading="lazy"
        />
        <span className="user-card__type-badge">{user.type}</span>
      </div>

      <div className="user-card__name">{user.login}</div>
      <div className="user-card__username">@{user.login}</div>

      <a
        className="user-card__link"
        href={user.html_url}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`View ${user.login}'s GitHub profile`}
      >
        View Profile
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1={10} y1={14} x2={21} y2={3} />
        </svg>
      </a>
    </article>
  );
}
