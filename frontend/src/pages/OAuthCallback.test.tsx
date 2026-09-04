import { render, screen, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { MemoryRouter } from "react-router-dom";
import OAuthCallback from "./OAuthCallback";
import authReducer from "../store/authSlice";

const createMockStore = () => configureStore({
  reducer: { auth: authReducer },
  preloadedState: {
    auth: { tokens: { github: null, gitlab: null, codeberg: null } }
  }
});

const renderComponent = (store: any, initialEntries: string[]) => {
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={initialEntries}>
        <OAuthCallback />
      </MemoryRouter>
    </Provider>
  );
};

describe("OAuthCallback", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  test("shows error if no code in URL", () => {
    const store = createMockStore();
    renderComponent(store, ["/oauth/callback"]);
    expect(screen.getByText("No authorization code found in the URL.")).toBeInTheDocument();
  });

  test("shows error if no provider in local storage", () => {
    const store = createMockStore();
    renderComponent(store, ["/oauth/callback?code=123"]);
    expect(screen.getByText("OAuth provider not found in local storage.")).toBeInTheDocument();
  });

  test("calls API and redirects on success", async () => {
    const store = createMockStore();
    localStorage.setItem("oauth_provider", "github");
    
    const fetchMock = vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ token: "test-token", provider: "github" }),
    } as any);

    renderComponent(store, ["/oauth/callback?code=123"]);

    expect(screen.getByText("Completing authentication...")).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });
    
    // After success, it navigates to "/", which is handled by MemoryRouter
    // and the token is dispatched. We can verify store state.
    expect(store.getState().auth.tokens.github).toBe("test-token");
    expect(localStorage.getItem("oauth_provider")).toBeNull();
  });

  test("shows error on API failure", async () => {
    const store = createMockStore();
    localStorage.setItem("oauth_provider", "github");
    
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: "Invalid code" }),
    } as any);

    renderComponent(store, ["/oauth/callback?code=123"]);

    await waitFor(() => {
      expect(screen.getByText("Invalid code")).toBeInTheDocument();
    });
  });
});
