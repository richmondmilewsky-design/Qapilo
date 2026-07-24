import { storage } from "@/src/utils/storage";

const BASE = process.env.EXPO_PUBLIC_BACKEND_URL;
const TOKEN_KEY = "tq_token";

let currentLang = "en";
export function setApiLang(lang: string) {
  currentLang = lang || "en";
}
export function getApiLang() {
  return currentLang;
}

export async function getToken(): Promise<string> {
  return (await storage.secureGet(TOKEN_KEY, "")) || "";
}

export async function setToken(token: string | null) {
  if (token) await storage.secureSet(TOKEN_KEY, token);
  else await storage.secureRemove(TOKEN_KEY);
}

type Opts = { method?: string; body?: any; auth?: boolean };

export async function apiRequest<T = any>(path: string, opts: Opts = {}): Promise<T> {
  const { method = "GET", body, auth = true } = opts;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) {
    const t = await getToken();
    if (t) headers.Authorization = `Bearer ${t}`;
  }
  let url = `${BASE}/api${path}`;
  if (method === "GET") {
    url += (path.includes("?") ? "&" : "?") + `lang=${currentLang}`;
  }
  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let detail = data && data.detail;
    if (Array.isArray(detail)) {
      detail = detail.map((d: any) => d?.msg || d?.detail || "").filter(Boolean).join(", ");
    }
    throw new Error(detail || (data && data.message) || "Something went wrong");
  }
  return data as T;
}
