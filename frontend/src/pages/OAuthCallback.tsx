import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setToken } from "../store/authSlice";

const OAuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const code = params.get("code");
    // We pass the provider in the URL state or use a specific callback route
    // But since GitHub only supports one redirect_uri per app typically, we might need a single callback
    // Wait, let's assume we pass the provider as a query parameter or path param
    // Let's grab provider from localStorage since the user initiated it
    const provider = localStorage.getItem("oauth_provider");

    if (!code) {
      setError("No authorization code found in the URL.");
      return;
    }
    if (!provider) {
      setError("OAuth provider not found in local storage.");
      return;
    }

    const exchangeToken = async () => {
      try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
        const redirectUri = `${window.location.origin}/oauth/callback`;
        const response = await fetch(`${baseUrl}/api/auth/${provider}/callback/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code,
            redirect_uri: redirectUri,
          }),
        });

        const data = await response.json();
        
        if (response.ok && data.token) {
          dispatch(setToken({ provider: data.provider, token: data.token }));
          localStorage.removeItem("oauth_provider");
          navigate("/"); // Redirect back to home
        } else {
          setError(data.error || "Failed to authenticate.");
        }
      } catch (err) {
        setError("Network error occurred during authentication.");
      }
    };

    exchangeToken();
  }, [location, dispatch, navigate]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <h2 className="text-2xl font-bold text-red-500 mb-4">Authentication Error</h2>
        <p className="text-gray-400 mb-6">{error}</p>
        <button
          onClick={() => navigate("/")}
          className="px-4 py-2 bg-[var(--primary-color)] text-white rounded-md hover:bg-opacity-80 transition-colors"
        >
          Return Home
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh]">
      <div className="w-8 h-8 border-4 border-t-[var(--primary-color)] border-[var(--surface-light)] rounded-full animate-spin mb-4"></div>
      <p className="text-[var(--text-secondary)]">Completing authentication...</p>
    </div>
  );
};

export default OAuthCallback;
