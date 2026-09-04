import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface AuthState {
  tokens: {
    github: string | null;
    gitlab: string | null;
    codeberg: string | null;
  };
}

const initialState: AuthState = {
  tokens: {
    github: null,
    gitlab: null,
    codeberg: null,
  },
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setToken(state, action: PayloadAction<{ provider: string; token: string }>) {
      const { provider, token } = action.payload;
      if (provider === "github" || provider === "gitlab" || provider === "codeberg") {
        state.tokens[provider] = token;
      }
    },
    logout(state, action: PayloadAction<{ provider: string }>) {
      const { provider } = action.payload;
      if (provider === "github" || provider === "gitlab" || provider === "codeberg") {
        state.tokens[provider] = null;
      }
    },
  },
});

export const { setToken, logout } = authSlice.actions;
export default authSlice.reducer;
