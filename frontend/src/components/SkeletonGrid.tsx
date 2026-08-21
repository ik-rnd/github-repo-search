/** Skeleton card displayed during loading */
function SkeletonCard() {
  return (
    <div className="skeleton-card" aria-hidden="true">
      <div className="skeleton-card__header">
        <div className="skeleton-line skeleton-line--avatar" />
        <div className="skeleton-card__header-text">
          <div className="skeleton-line skeleton-line--title" />
          <div className="skeleton-line skeleton-line--text-short" />
        </div>
      </div>
      <div className="skeleton-line skeleton-line--text" />
      <div className="skeleton-line skeleton-line--text" />
      <div className="skeleton-line skeleton-line--text-short" />
    </div>
  );
}

interface SkeletonGridProps {
  count?: number;
}

export default function SkeletonGrid({ count = 9 }: SkeletonGridProps) {
  return (
    <div
      className="skeleton-grid"
      aria-busy="true"
      aria-label="Loading results…"
      role="status"
    >
      {Array.from({ length: count }, (_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
