import { env } from "../lib/env";
import {
  GOALS,
  ApiError,
  type Match,
  type MatchRequest,
  type FeedbackRequest,
  type FeedbackResponse,
  type ProfileMe,
  type HealthResponse,
  type TelegramLinkResponse,
  type MatchResult,
  type Goal,
} from "../types";
import { mockApi } from "./mockApi";
import { supabase } from "./supabase";
export { ApiError };
export type { MatchResult } from "../types";

const normalizeGoal = (g: string): Goal => {
  if (g === "offer_mentorship") return "be_mentor";
  if (g === "find_investor") return "exchange_experience";
  return g as Goal;
};

export function validateMatches(data: unknown): MatchResult {
  if (
    !data ||
    typeof data !== "object" ||
    !("matches" in data) ||
    !Array.isArray(data.matches)
  )
    throw new ApiError(502, "errors.invalid");
  const matches = data.matches.filter((m: unknown): m is Match => {
    const p = m as Match | null;
    if (p && typeof p.goal === "string") {
      p.goal = normalizeGoal(p.goal);
    }
    const valid =
      p &&
      ["id", "name", "role", "reason", "icebreaker"].every(
        (k) =>
          typeof p[k as keyof Match] === "string" &&
          String(p[k as keyof Match]).trim().length > 0,
      ) &&
      typeof p.score === "number" &&
      Number.isFinite(p.score) &&
      p.score >= 0 &&
      p.score <= 100 &&
      GOALS.includes(p.goal);
    if (!valid) console.warn("Discarded invalid match response item");
    return Boolean(valid);
  });
  if (data.matches.length && !matches.length)
    throw new ApiError(502, "errors.invalid");
  const ms = "processing_ms" in data ? data.processing_ms : undefined;
  return {
    matches: matches.slice(0, 5),
    ...(typeof ms === "number" && Number.isFinite(ms) && ms >= 0
      ? { processing_ms: ms }
      : {}),
  };
}

export async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; timeout?: number } = {},
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeout ?? 15000);
  try {
    const session = supabase
      ? (await supabase.auth.getSession()).data.session
      : null;
    const res = await fetch(`${env.apiBaseUrl}${path}`, {
      method: options.method ?? "GET",
      headers: {
        "Content-Type": "application/json",
        ...(session ? { Authorization: `Bearer ${session.access_token}` } : {}),
      },
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: controller.signal,
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        await supabase?.auth.signOut();
        window.dispatchEvent(new Event("meetmatch:unauthorized"));
      }
      const detail =
        data?.detail ?? data?.error?.details ?? data?.error?.message;
      throw new ApiError(
        res.status,
        res.status >= 500
          ? "errors.server"
          : res.status === 401 || res.status === 403
            ? "errors.auth"
            : res.status === 422
              ? "errors.validation"
              : "errors.request",
        detail,
      );
    }
    return data as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    throw new ApiError(0, "errors.network");
  } finally {
    clearTimeout(timer);
  }
}

const realApi = {
  health: () => request<HealthResponse>("/api/health"),
  match: async (p: MatchRequest) => {
    const backendGoal = p.goal === "be_mentor" ? "offer_mentorship" : p.goal;
    const body = {
      name: "",
      role: p.role,
      goal: backendGoal,
      skills: p.stack ?? [],
      interests: p.interests ?? [],
      experience_years: Math.round(Number(p.experience ?? 0)),
      bio: p.about ?? "",
    };
    return validateMatches(
      await request<unknown>("/api/match", {
        method: "POST",
        body,
        timeout: 10000,
      }),
    );
  },
  feedback: async (p: FeedbackRequest) => {
    const action =
      p.action === "met" ? "like" : p.action === "not_fit" ? "dislike" : p.action;
    const r = await request<FeedbackResponse>("/api/feedback", {
      method: "POST",
      body: { match_id: p.match_id, action },
    });
    if (r?.ok !== true) throw new ApiError(502, "errors.invalid");
    return r;
  },
  getProfile: async (): Promise<ProfileMe> => {
    const res = await request<{ profile?: any } | ProfileMe>("/api/profile/me");
    if (!res) return {};
    const p = "profile" in res ? res.profile : res;
    if (!p) return {};
    return {
      email: p.email,
      personal: {
        full_name: p.name || p.personal?.full_name || "",
        age: p.age ?? p.personal?.age ?? 20,
        city: p.city || p.personal?.city || "",
        phone: p.phone || p.personal?.phone || "",
        gender: p.gender ?? p.personal?.gender ?? null,
      },
      professional: {
        role: p.role || p.professional?.role || "",
        stack: p.skills || p.professional?.stack || [],
        experience: p.experience_years ?? p.professional?.experience ?? 0,
        interests: p.interests || p.professional?.interests || [],
        about: p.bio || p.professional?.about || "",
        goal: normalizeGoal(p.goal || p.professional?.goal || "find_job"),
      },
      stats: p.stats,
    };
  },
  updateProfile: async (p: Partial<ProfileMe>): Promise<ProfileMe> => {
    const goal =
      p.professional?.goal === "be_mentor"
        ? "offer_mentorship"
        : p.professional?.goal || "find_job";
    const body: Record<string, unknown> = {
      name: p.personal?.full_name ?? "",
      role: p.professional?.role ?? "Attendee",
      goal,
      skills: p.professional?.stack ?? [],
      interests: p.professional?.interests ?? [],
      experience_years: p.professional?.experience ?? 0,
      bio: p.professional?.about ?? "",
    };
    if (p.email) body.email = p.email;
    if (p.personal?.phone) body.phone = p.personal.phone;
    if (p.personal?.age !== undefined) body.age = p.personal.age;
    if (p.personal?.city) body.city = p.personal.city;

    const res = await request<{ profile?: any } | ProfileMe>("/api/profile/me", {
      method: "PUT",
      body,
    });
    const saved = res && "profile" in res ? res.profile : res;
    return {
      ...p,
      email: saved?.email ?? p.email,
      personal: {
        full_name: saved?.name || p.personal?.full_name || "",
        age: saved?.age ?? p.personal?.age ?? 20,
        city: saved?.city || p.personal?.city || "",
        phone: saved?.phone || p.personal?.phone || "",
        gender: p.personal?.gender ?? null,
      },
      professional: {
        role: saved?.role || p.professional?.role || "",
        stack: saved?.skills || p.professional?.stack || [],
        experience: saved?.experience_years ?? p.professional?.experience ?? 0,
        interests: saved?.interests || p.professional?.interests || [],
        about: saved?.bio || p.professional?.about || "",
        goal: normalizeGoal(saved?.goal || p.professional?.goal || "find_job"),
      },
    };
  },
  linkTelegram: async (): Promise<TelegramLinkResponse> => {
    const r = await request<{
      code: string;
      expires_in?: number;
      expires_in_seconds?: number;
      deep_link?: string;
    }>("/api/telegram/link", { method: "POST" });
    return {
      code: r.code,
      expires_in: r.expires_in ?? r.expires_in_seconds,
      deep_link: r.deep_link,
    };
  },
};
export const api = env.useMockApi ? mockApi : realApi;
