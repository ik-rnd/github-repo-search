import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import RepoCard from "./RepoCard";
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

test("renders star and fork buttons with correct links", () => {
  render(<RepoCard repo={mockRepo} />);

  const starLink = screen.getByLabelText("1000 stars");
  expect(starLink).toHaveAttribute("href", "https://github.com/vitest-dev/vitest/stargazers");
  expect(starLink).toHaveAttribute("target", "_blank");

  const forkLink = screen.getByLabelText("500 forks");
  expect(forkLink).toHaveAttribute("href", "https://github.com/vitest-dev/vitest/forks");
  expect(forkLink).toHaveAttribute("target", "_blank");
});
