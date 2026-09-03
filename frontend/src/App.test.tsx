import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { Provider } from "react-redux";
import { store } from "./store";
import App from "./App";

test("renders hero title when idle", () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );

  expect(screen.getByText("Search Git")).toBeInTheDocument();
  expect(screen.getByText("Find repositories and developers across millions of projects.")).toBeInTheDocument();
});
