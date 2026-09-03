import { useCallback, useEffect, useRef } from "react";
import debounce from "lodash/debounce";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  setQuery,
  setProvider,
  setEntityType,
  fetchResults,
  clearResults,
  buildCacheKey,
} from "../store/searchSlice";
import type { EntityType, GitProvider } from "../types";

const MIN_QUERY_LENGTH = 3;
const DEBOUNCE_DELAY_MS = 400;

interface SearchBarProps {
  compact?: boolean;
}

export default function SearchBar({ compact = false }: SearchBarProps) {
  const dispatch = useAppDispatch();
  const query = useAppSelector((s) => s.search.query);
  const provider = useAppSelector((s) => s.search.provider);
  const entityType = useAppSelector((s) => s.search.entityType);
  const cache = useAppSelector((s) => s.search.cache);

  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search — recreated only when dispatch changes (stable)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce((q: string, type: EntityType, prov: GitProvider) => {
      if (q.length >= MIN_QUERY_LENGTH) {
        const cacheKey = buildCacheKey(prov, q, type);
        if (!cache[cacheKey]) {
          dispatch(fetchResults({ query: q, entityType: type, provider: prov }));
        } else {
          // Serve from front-end cache immediately
          dispatch(fetchResults({ query: q, entityType: type, provider: prov }));
        }
      } else {
        dispatch(clearResults());
      }
    }, DEBOUNCE_DELAY_MS),
    [dispatch]
  );

  // Cancel debounce on unmount
  useEffect(() => () => debouncedSearch.cancel(), [debouncedSearch]);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    dispatch(setQuery(value));
    debouncedSearch(value, entityType, provider);
  };

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProv = e.target.value as GitProvider;
    dispatch(setProvider(newProv));
    if (query.length >= MIN_QUERY_LENGTH) {
      debouncedSearch.cancel();
      dispatch(fetchResults({ query, entityType, provider: newProv }));
    }
  };

  const handleEntityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const type = e.target.value as EntityType;
    dispatch(setEntityType(type));
    // Immediately re-fetch if enough characters already typed
    if (query.length >= MIN_QUERY_LENGTH) {
      debouncedSearch.cancel();
      dispatch(fetchResults({ query, entityType: type, provider }));
    }
  };

  const handleClear = () => {
    dispatch(setQuery(""));
    dispatch(clearResults());
    inputRef.current?.focus();
  };

  const wrapperClass = compact ? "search-controls--compact" : "search-controls--hero";

  return (
    <div className={`search-controls ${wrapperClass}`} role="search">
      <div className="search-input-wrapper">
        {/* Search icon */}
        <svg
          className="search-input-icon"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx={11} cy={11} r={8} />
          <line x1={21} y1={21} x2={16.65} y2={16.65} />
        </svg>

        <input
          id="search-input"
          ref={inputRef}
          type="search"
          className="search-input"
          placeholder="Type at least 3 characters to start searching"
          value={query}
          onChange={handleQueryChange}
          autoFocus
          autoComplete="off"
          aria-label="Search Git users or repositories"
          aria-describedby="search-hint"
        />

        {query && (
          <button
            className="search-clear-btn"
            onClick={handleClear}
            aria-label="Clear search"
            title="Clear"
          >
            <svg
              width={14}
              height={14}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2.5}
              strokeLinecap="round"
              aria-hidden="true"
            >
              <line x1={18} y1={6} x2={6} y2={18} />
              <line x1={6} y1={6} x2={18} y2={18} />
            </svg>
          </button>
        )}
      </div>

      <select
        id="provider-select"
        className="search-dropdown"
        value={provider}
        onChange={handleProviderChange}
        aria-label="Git provider"
      >
        <option value="codeberg">Codeberg</option>
        <option value="github">GitHub</option>
        <option value="gitlab">GitLab</option>
      </select>

      <select
        id="entity-type-select"
        className="search-dropdown"
        value={entityType}
        onChange={handleEntityChange}
        aria-label="Entity type"
      >
        <option value="repositories">Repositories</option>
        <option value="users">Users</option>
      </select>
    </div>
  );
}
