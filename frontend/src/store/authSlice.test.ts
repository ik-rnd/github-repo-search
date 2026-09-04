import { expect, test, describe } from "vitest";
import authReducer, { setToken, logout, AuthState } from "./authSlice";

describe("authSlice", () => {
  const initialState: AuthState = {
    tokens: {
      github: null,
      gitlab: null,
      codeberg: null,
    },
  };

  test("should handle initial state", () => {
    expect(authReducer(undefined, { type: "unknown" })).toEqual(initialState);
  });

  test("should handle setToken for github", () => {
    const actual = authReducer(initialState, setToken({ provider: "github", token: "test-token" }));
    expect(actual.tokens.github).toEqual("test-token");
  });

  test("should ignore setToken for unknown provider", () => {
    const actual = authReducer(initialState, setToken({ provider: "unknown", token: "test-token" } as any));
    expect(actual).toEqual(initialState);
  });

  test("should handle logout for github", () => {
    const loggedInState: AuthState = {
      tokens: {
        github: "test-token",
        gitlab: null,
        codeberg: null,
      },
    };
    const actual = authReducer(loggedInState, logout({ provider: "github" }));
    expect(actual.tokens.github).toBeNull();
  });
});
