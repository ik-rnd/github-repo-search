import { useState } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { logout } from "../store/authSlice";
import GitHubLogo from "./GitHubLogo";

export default function Header() {
  const dispatch = useAppDispatch();
  const tokens = useAppSelector((s) => (s as any).auth?.tokens || { github: null, gitlab: null, codeberg: null });
  const [showAuth, setShowAuth] = useState(false);

  const handleLogin = async (provider: string) => {
    localStorage.setItem("oauth_provider", provider);
    try {
      const redirectUri = encodeURIComponent(`${window.location.origin}/oauth/callback`);
      const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
      const res = await fetch(`${baseUrl}/api/auth/${provider}/login/?redirect_uri=${redirectUri}`);
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (e) {
      console.error("Login failed", e);
    }
  };

  const handleLogout = (provider: string) => {
    dispatch(logout({ provider }));
  };

  const providers = [
    { id: "github", name: "GitHub" },
    { id: "gitlab", name: "GitLab" },
    { id: "codeberg", name: "Codeberg" },
  ];

  return (
    <header className="header flex justify-between items-center px-6 py-4 border-b border-[var(--border-color)]" role="banner">
      <div className="flex items-center gap-4">
        <GitHubLogo className="header__logo w-8 h-8" />
        <div className="header__text">
          <h1 className="text-xl font-bold m-0 leading-tight">Git Searcher</h1>
          <p className="text-sm text-[var(--text-secondary)] m-0">Search users or repositories</p>
        </div>
      </div>
      
      <div className="relative">
        <button 
          onClick={() => setShowAuth(!showAuth)}
          className="px-4 py-2 bg-[var(--surface-light)] border border-[var(--border-color)] rounded-md hover:bg-[var(--surface-hover)] transition-colors"
        >
          Accounts
        </button>
        
        {showAuth && (
          <div className="absolute right-0 mt-2 w-48 bg-[var(--surface-color)] border border-[var(--border-color)] rounded-md shadow-lg z-50">
            <div className="p-2 flex flex-col gap-2">
              {providers.map(p => {
                const isLoggedIn = !!tokens[p.id as keyof typeof tokens];
                return (
                  <div key={p.id} className="flex justify-between items-center text-sm p-2 rounded hover:bg-[var(--surface-light)]">
                    <span className="font-medium text-[var(--text-primary)]">{p.name}</span>
                    {isLoggedIn ? (
                      <button onClick={() => handleLogout(p.id)} className="text-red-400 hover:text-red-300">Logout</button>
                    ) : (
                      <button onClick={() => handleLogin(p.id)} className="text-[var(--primary-color)] hover:opacity-80">Login</button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
