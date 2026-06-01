export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export type Opportunity = {
  id: number;
  title: string;
  category: string | null;
  demand_score: number;
  margin_score: number;
  competition_score: number;
  catalog_match_score: number;
  risk_score: number;
  opportunity_score: number;
  listing_difficulty: string;
  risk_level: string;
  recommended_action: string;
  confidence: string;
  created_at: string;
  target_audience?: string | null;
  lifecycle_stage?: string | null;
  seasonality?: string | null;
  top_features?: string[] | null;
  differentiation?: string | null;
};

export function token() {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem("wm_token") ?? "";
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const saved = token();
  if (saved) headers.set("Authorization", `Bearer ${saved}`);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers, cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const scoreColor = (score: number) => {
  if (score >= 80) return "text-ok";
  if (score >= 60) return "text-warn";
  return "text-danger";
};
