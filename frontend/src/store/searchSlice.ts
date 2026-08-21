import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { searchGitHub } from "../api/searchApi";
import type { CachedResult, EntityType, SearchItem, SearchState } from "../types";

// ---- Async thunk ----

export const fetchResults = createAsyncThunk(
  "search/fetchResults",
  async (
    { query, entityType }: { query: string; entityType: EntityType },
    { rejectWithValue }
  ) => {
    try {
      const data = await searchGitHub(query, entityType);
      return data;
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } };
        return rejectWithValue(
          axiosErr.response?.data?.error ?? "An unexpected error occurred."
        );
      }
      return rejectWithValue("Network error — please check your connection.");
    }
  }
);

// ---- Initial state ----

const initialState: SearchState = {
  query: "",
  entityType: "repositories",
  status: "idle",
  error: null,
  totalCount: 0,
  items: [] as SearchItem[],
  cache: {},
  fromCache: false,
};

// ---- Cache key helper ----

export const buildCacheKey = (query: string, entityType: EntityType): string =>
  `${query.toLowerCase().trim()}:${entityType}`;

// ---- Slice ----

const searchSlice = createSlice({
  name: "search",
  initialState,
  reducers: {
    setQuery(state, action: PayloadAction<string>) {
      state.query = action.payload;
    },
    setEntityType(state, action: PayloadAction<EntityType>) {
      state.entityType = action.payload;
    },
    clearResults(state) {
      state.status = "idle";
      state.items = [];
      state.totalCount = 0;
      state.error = null;
      state.fromCache = false;
    },
    clearCache(state) {
      state.cache = {};
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchResults.pending, (state, action) => {
        const { query, entityType } = action.meta.arg;
        const cacheKey = buildCacheKey(query, entityType);
        const cached = state.cache[cacheKey] as CachedResult | undefined;

        if (cached) {
          // Serve from in-memory cache without showing loading state
          state.items = cached.items;
          state.totalCount = cached.total_count;
          state.fromCache = true;
          state.status = "success";
          state.error = null;
        } else {
          state.status = "loading";
          state.error = null;
          state.fromCache = false;
        }
      })
      .addCase(fetchResults.fulfilled, (state, action) => {
        const { query, entityType } = action.meta.arg;
        const cacheKey = buildCacheKey(query, entityType);

        // Only update if this is actually a fresh result (not pre-empted by cache)
        if (!state.fromCache) {
          state.status = "success";
          state.items = action.payload.items;
          state.totalCount = action.payload.total_count;
          state.error = null;
        }

        // Always populate / refresh the cache entry
        state.cache[cacheKey] = {
          items: action.payload.items,
          total_count: action.payload.total_count,
          cached: action.payload.cached,
        };
      })
      .addCase(fetchResults.rejected, (state, action) => {
        // Don't override a cached result with an error
        if (!state.fromCache) {
          state.status = "error";
          state.error = (action.payload as string) ?? "Something went wrong.";
          state.items = [];
          state.totalCount = 0;
        }
      });
  },
});

export const { setQuery, setEntityType, clearResults, clearCache: clearReduxCache } =
  searchSlice.actions;

export default searchSlice.reducer;
