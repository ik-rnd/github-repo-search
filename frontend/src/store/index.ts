import { combineReducers, configureStore } from "@reduxjs/toolkit";
import {
  FLUSH,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
  REHYDRATE,
  persistReducer,
  persistStore,
} from "redux-persist";
import storage from "redux-persist/lib/storage";
import searchReducer from "./searchSlice";
import authReducer from "./authSlice";

const persistConfig = {
  key: "github-searcher",
  version: 1,
  storage,
  // Persist only the cache; do NOT persist status/error so the UI starts fresh
  whitelist: ["cache"],
};

const rootReducer = combineReducers({
  search: persistReducer(persistConfig, searchReducer),
  auth: persistReducer({ key: 'github-auth', version: 1, storage }, authReducer),
});

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

export const persistor = persistStore(store);

// Typed hooks helpers
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
