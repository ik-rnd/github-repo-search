import { useAppSelector } from "./store/hooks";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import ResultsGrid from "./components/ResultsGrid";
import GitHubLogo from "./components/GitHubLogo";

export default function App() {
  const { query, entityType, status } = useAppSelector((s) => s.search);

  // Show results area when we have a meaningful query or results
  const hasContent = query.length >= 3 && status !== "idle";

  return (
    <div className="app">
      <Header />

      <main className="page" id="main-content">
        {hasContent ? (
          /* ---- Compact layout: search bar at top, results below ---- */
          <>
            <SearchBar compact />
            <ResultsGrid entityType={entityType} />
          </>
        ) : (
          /* ---- Hero / centred layout when no query ---- */
          <div className="hero">
            <div className="hero__icon" aria-hidden="true">
              <GitHubLogo />
            </div>

            <div>
              <h2 className="hero__title">Search Git</h2>
              <p className="hero__subtitle">
                Find repositories and developers across millions of projects.
              </p>
            </div>

            <div className="hero__search-wrapper">
              <SearchBar />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
