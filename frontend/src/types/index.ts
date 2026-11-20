// ===== Цели =====
export const GOALS = [
  "find_job",
  "hire",
  "find_mentor",
  "be_mentor",
  "find_cofounder",
  "exchange_experience",
] as const;
export type Goal = (typeof GOALS)[number];

// ===== /api/match (контракт из ТЗ) =====
export interface MatchRequest {
  role: string;
  stack: string[];
  experience: number; // годы
  interests: string[];
  about: string;
  goal: Goal;
}

export interface Match {
  id: string; // например "user_042"
  name: string;
  role: string;
  score: number; // 0–100, считает Backend
  goal: Goal; // цель участника-рекомендации
  reason: string; // 1–2 предложения
  icebreaker: string; // первая фраза
}

export interface MatchResponse {
  matches: Match[]; // до 5 элементов
  processing_ms: number;
}

// UI transport tolerates missing timing; demo provenance never changes match scores.
export type MatchResult = Omit<MatchResponse, "processing_ms"> & {
  processing_ms?: number;
  __demo?: boolean;
};

// ===== /api/feedback =====
// [ПРЕДПОЛОЖЕНИЕ] Схема не зафиксирована в ТЗ. Сверить с Backend (Pydantic).
export type FeedbackAction = "met" | "not_fit";

export interface FeedbackRequest {
  match_id: string;
  action: FeedbackAction;
}

export interface FeedbackResponse {
  ok: boolean;
}

// ===== /api/profile/me =====
// [ПРЕДПОЛОЖЕНИЕ] Схема не зафиксирована в ТЗ. Сверить с Backend.
export type Gender = "male" | "female" | "prefer_not_to_say";

export interface PersonalProfile {
  full_name: string;
  age: number;
  gender: Gender | null;
  city: string;
  phone: string;
}

export interface ProfessionalProfile extends MatchRequest {}

export interface ProfileMe {
  email?: string;
  personal?: PersonalProfile;
  professional?: ProfessionalProfile;
  // Статистика — только если Backend её отдаёт; Frontend ничего не выдумывает.
  stats?: Record<string, number>;
}

// ===== /api/telegram/link =====
// [ПРЕДПОЛОЖЕНИЕ] Одноразовый код привязки. Сверить с Backend.
export interface TelegramLinkResponse {
  code: string;
  deep_link?: string; // t.me/<bot>?start=<code> — только одноразовый код, без токенов
  expires_in?: number; // секунды
}

// ===== /api/health =====
export interface HealthResponse {
  status: string;
}

// ===== Ошибки =====
export class ApiError extends Error {
  constructor(
    public status: number, // 0 — сетевая ошибка/таймаут
    message: string,
    public detail?: unknown,
  ) {
    super(message);
  }
}

// ===== UI-состояния =====
export type MatchesStatus =
  "idle" | "loading" | "success" | "partial" | "empty" | "error";
export type MatchCardStatus = "idle" | "sending" | "met" | "rejected";
export type Lang = "ru" | "kk" | "en";
