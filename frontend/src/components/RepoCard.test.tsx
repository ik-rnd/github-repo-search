import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi } from "vitest";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import RepoCard from "./RepoCard";
import authReducer from "../store/authSlice";
import searchReducer from "../store/searchSlice";
import type { GitHubRepository } from "../types";

const mockRepo: GitHubRepository = {
  id: 1,
  name: "vitest",
  full_name: "vitest-dev/vitest",
  description: "A Vite-native test framework",
  html_url: "https://github.com/vitest-dev/vitest",
  stargazers_count: 1000,
  forks_count: 500,
  open_issues_count: 10,
  language: "TypeScript",
  owner: {
    login: "vitest-dev",
    avatar_url: "https://avatars.githubusercontent.com/u/12345",
    html_url: "https://github.com/vitest-dev",
  },
  updated_at: "2024-01-01T00:00:00Z",
  watchers_count: 1000,
  topics: ["testing", "vite"],
};

const createMockStore = (provider: string, token: string | null) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      search: searchReducer,
    },
    preloadedState: {
      auth: {
        tokens: {
          github: token,
          gitlab: null,
          codeberg: null,
        },
      },
      search: {
        provider,
        query: "",
        entityType: "repositories",
        cache: true,
      },
    } as any,
  });
};

describe("RepoCard", () => {
  test("renders correctly", () => {
    const store = createMockStore("github", null);
    render(
      <Provider store={store}>
        <RepoCard repo={mockRepo} />
      </Provider>
    );
    expect(screen.getByText("vitest")).toBeInTheDocument();
  });

  test("opens repository URL in a new tab when clicking star", () => {
    const store = createMockStore("github", null);
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);

    render(
      <Provider store={store}>
        <RepoCard repo={mockRepo} />
      </Provider>
    );

    const starBtn = screen.getByLabelText("1000 stars");
    fireEvent.click(starBtn);

    expect(openMock).toHaveBeenCalledWith(
      "https://github.com/vitest-dev/vitest",
      "_blank",
      "noopener,noreferrer"
    );

    openMock.mockRestore();
  });
});
