import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { Platform } from "react-native";
import * as WebBrowser from "expo-web-browser";
import * as Linking from "expo-linking";
import { apiRequest, setToken } from "@/src/api/client";

export type User = {
  user_id: string;
  email: string;
  name: string;
  picture: string | null;
  xp: number;
  level: number;
  level_current: number;
  level_needed: number;
  streak: number;
  longest_streak: number;
  completed_lessons: string[];
  perfect_lessons: string[];
  badges: string[];
  daily_xp: number;
  daily_goal: number;
  auth_provider: string;
  is_pro: boolean;
  pro_source: "trial" | "subscription" | "free";
  in_trial: boolean;
  trial_days_left: number;
  trial_ends_at: string | null;
  subscription_status: string | null;
};

type AuthCtx = {
  user: User | null;
  loading: boolean;
  signup: (email: string, password: string, name: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  setUser: (u: User) => void;
};

const Ctx = createContext<AuthCtx>({} as AuthCtx);
export const useAuth = () => useContext(Ctx);

WebBrowser.maybeCompleteAuthSession();

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await apiRequest<{ user: User }>("/auth/me");
      setUser(data.user);
    } catch {
      await setToken(null);
      setUser(null);
    }
  }, []);

  const extractSessionId = (url: string): string | null => {
    if (!url) return null;
    const parsed = Linking.parse(url);
    if (parsed.queryParams?.session_id) return parsed.queryParams.session_id as string;
    if (url.includes("session_id=")) {
      return url.split("session_id=")[1].split(/[&#]/)[0];
    }
    return null;
  };

  useEffect(() => {
    let sub: any;
    (async () => {
      // 1) Web: process session_id returned in the URL (hash or query) first.
      if (Platform.OS === "web" && typeof window !== "undefined") {
        const raw = window.location.hash || window.location.search;
        const sid = extractSessionId(raw);
        if (sid) {
          try {
            await exchangeSession(sid);
          } catch {}
          window.history.replaceState(null, "", window.location.pathname);
          setLoading(false);
          return;
        }
      }
      // 2) Mobile: cold-start deep link fallback.
      if (Platform.OS !== "web") {
        const initial = await Linking.getInitialURL();
        const sid = initial ? extractSessionId(initial) : null;
        if (sid) {
          try {
            await exchangeSession(sid);
          } catch {}
          setLoading(false);
          return;
        }
        sub = Linking.addEventListener("url", async ({ url }) => {
          const s = extractSessionId(url);
          if (s) {
            try {
              await exchangeSession(s);
            } catch {}
          }
        });
      }
      // 3) Otherwise resume an existing session.
      await refresh();
      setLoading(false);
    })();
    return () => {
      if (sub?.remove) sub.remove();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refresh]);

  const signup = async (email: string, password: string, name: string) => {
    const data = await apiRequest<{ token: string; user: User }>("/auth/signup", {
      method: "POST",
      auth: false,
      body: { email, password, name },
    });
    await setToken(data.token);
    setUser(data.user);
  };

  const login = async (email: string, password: string) => {
    const data = await apiRequest<{ token: string; user: User }>("/auth/login", {
      method: "POST",
      auth: false,
      body: { email, password },
    });
    await setToken(data.token);
    setUser(data.user);
  };

  const exchangeSession = async (sessionId: string) => {
    const data = await apiRequest<{ token: string; user: User }>("/auth/google", {
      method: "POST",
      auth: false,
      body: { session_id: sessionId },
    });
    await setToken(data.token);
    setUser(data.user);
  };

  const loginWithGoogle = async () => {
    const redirectUrl =
      Platform.OS === "web" ? window.location.origin + "/" : Linking.createURL("");
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;

    if (Platform.OS === "web") {
      window.location.href = authUrl;
      return;
    }
    const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
    if (result.type === "success" && result.url) {
      const parsed = Linking.parse(result.url);
      let sessionId =
        (parsed.queryParams?.session_id as string) || null;
      if (!sessionId && result.url.includes("session_id=")) {
        const frag = result.url.split("session_id=")[1];
        sessionId = frag.split(/[&#]/)[0];
      }
      if (sessionId) await exchangeSession(sessionId);
    }
  };

  const logout = async () => {
    try {
      await apiRequest("/auth/logout", { method: "POST" });
    } catch {}
    await setToken(null);
    setUser(null);
  };

  return (
    <Ctx.Provider
      value={{ user, loading, signup, login, loginWithGoogle, logout, refresh, setUser }}
    >
      {children}
    </Ctx.Provider>
  );
}
