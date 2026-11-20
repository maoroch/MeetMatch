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
  exclude_ids?: string[];
  preferred_slots?: string[];
}

export interface Match {
  id: string; // например "user_042"
  name: string;
  role: string;
  score: number; // 0–100, считает Backend
  goal: Goal; // цель участника-рекомендации
  reason: string; // 1–2 предложения
  icebreaker: string; // первая фраза
  available_slots?: string[];
  suggested_slot?: string;
}

export interface PartnerBooth {
  id: string;
  name: string;
  category: string;
  location: string;
  tags: string[];
  reason: string;
  match_score: number;
}

export interface MatchResponse {
  matches: Match[]; // до 5 элементов
  processing_ms: number;
  recommended_booths?: PartnerBooth[];
}

// UI transport tolerates missing timing; demo provenance never changes match scores.
export type MatchResult = Omit<MatchResponse, "processing_ms"> & {
  processing_ms?: number;
  __demo?: boolean;
};

// ===== /api/organizer/stats =====
export interface OrganizerStatItem {
  name: string;
  count: number;
  share: number;
}

export interface OrganizerGoalItem {
  goal: string;
  count: number;
  share: number;
}

export interface OrganizerBoothStat {
  id: string;
  name: string;
  category: string;
  location: string;
  tags: string[];
  matching_participants: number;
}

export interface OrganizerStats {
  total_participants: number;
  total_feedback: number;
  met_count: number;
  not_fit_count: number;
  goals: OrganizerGoalItem[];
  top_skills: OrganizerStatItem[];
  top_interests: OrganizerStatItem[];
  top_roles: OrganizerStatItem[];
  experience_buckets: OrganizerStatItem[];
  booths: OrganizerBoothStat[];
}

// ===== /api/feedback =====
export type FeedbackAction = "met" | "not_fit";

export interface FeedbackRequest {
  match_id: string;
  action: FeedbackAction;
}

export interface FeedbackResponse {
  ok: boolean;
}

// ===== /api/profile/me =====
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
  stats?: Record<string, number>;
}

// ===== /api/telegram/link =====
export interface TelegramLinkResponse {
  code: string;
  deep_link?: string;
  expires_in?: number;
}

// ===== /api/health =====
export interface HealthResponse {
  status: string;
}

// ===== Ошибки =====
export class ApiError extends Error {
  constructor(
    public status: number,
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
