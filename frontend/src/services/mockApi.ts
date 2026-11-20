// DEMO ONLY — не реальный AI-подбор
import {
  ApiError,
  type Match,
  type MatchRequest,
  type FeedbackRequest,
  type ProfileMe,
  type OrganizerStats,
} from "../types";
export const demoMatches: Match[] = [
  {
    id: "demo-a",
    name: "Демо-профиль А.",
    role: "IT Recruiter",
    score: 96,
    goal: "hire",
    reason:
      "Демонстрационный пример: рекрутер ищет специалиста для продуктовой команды. Общий интерес к технологиям может стать темой для разговора.",
    icebreaker: "Какие навыки сейчас особенно ценятся в вашей команде?",
  },
  {
    id: "demo-b",
    name: "Демо-профиль Б.",
    role: "Product Designer",
    score: 92,
    goal: "exchange_experience",
    reason:
      "Демонстрационный пример: дизайнеру интересно обсудить продуктовый подход и обменяться опытом работы над интерфейсами.",
    icebreaker:
      "Какой продуктовый эксперимент больше всего повлиял на вашу работу?",
  },
  {
    id: "demo-c",
    name: "Демо-профиль В.",
    role: "Startup Founder",
    score: 89,
    goal: "find_cofounder",
    reason:
      "Демонстрационный пример: основатель ищет партнёра для нового проекта. Разговор поможет понять, совпадают ли ваши интересы и подход к работе.",
    icebreaker: "Какую проблему решает ваш проект и кого вы ищете в команду?",
  },
  {
    id: "demo-d",
    name: "Демо-профиль Г.",
    role: "Engineering Lead",
    score: 87,
    goal: "be_mentor",
    reason:
      "Демонстрационный пример: технический руководитель готов делиться опытом построения команд и развития инженерной карьеры.",
    icebreaker: "Какой совет вы дали бы себе в начале карьеры?",
  },
  {
    id: "demo-e",
    name: "Демо-профиль Д.",
    role: "Data Analyst",
    score: 84,
    goal: "find_mentor",
    reason:
      "Демонстрационный пример: аналитик ищет наставника и обсуждение практических задач с данными. Это статические данные, а не результат анализа анкеты.",
    icebreaker: "С какими задачами анализа данных вы сейчас работаете?",
  },
];
let profile: ProfileMe = {};
const feedback = new Map<string, string>();
const delay = () => new Promise((r) => setTimeout(r, 600));
export const mockApi = {
  async health() {
    return { status: "demo" };
  },
  async match(_request: MatchRequest) {
    await delay();
    return { matches: demoMatches.map((m) => ({ ...m })), __demo: true };
  },
  async feedback(req: FeedbackRequest) {
    await delay();
    feedback.set(req.match_id, req.action);
    return { ok: true };
  },
  async organizerStats(): Promise<OrganizerStats> {
    await delay();
    return {
      total_participants: 180,
      total_feedback: feedback.size,
      met_count: Array.from(feedback.values()).filter((v) => v === "met").length,
      not_fit_count: Array.from(feedback.values()).filter((v) => v === "not_fit").length,
      goals: [
        { goal: "find_job", count: 30, share: 16.7 },
        { goal: "hire", count: 30, share: 16.7 },
        { goal: "find_mentor", count: 30, share: 16.7 },
        { goal: "be_mentor", count: 30, share: 16.7 },
        { goal: "find_cofounder", count: 30, share: 16.7 },
        { goal: "exchange_experience", count: 30, share: 16.5 },
      ],
      top_skills: [
        { name: "Python", count: 68, share: 37.8 },
        { name: "TypeScript", count: 62, share: 34.4 },
        { name: "React", count: 58, share: 32.2 },
        { name: "FastAPI", count: 44, share: 24.4 },
        { name: "Machine Learning", count: 39, share: 21.7 },
        { name: "Docker", count: 35, share: 19.4 },
      ],
      top_interests: [
        { name: "AI", count: 74, share: 41.1 },
        { name: "Product", count: 61, share: 33.9 },
        { name: "Startups", count: 55, share: 30.6 },
        { name: "Architecture", count: 42, share: 23.3 },
        { name: "Mentorship", count: 38, share: 21.1 },
      ],
      top_roles: [
        { name: "Frontend Developer", count: 30, share: 16.7 },
        { name: "Backend Engineer", count: 30, share: 16.7 },
        { name: "ML Engineer", count: 30, share: 16.7 },
        { name: "Product Manager", count: 30, share: 16.7 },
      ],
      experience_buckets: [
        { name: "0–1", count: 36, share: 20.0 },
        { name: "2–4", count: 64, share: 35.6 },
        { name: "5–7", count: 48, share: 26.7 },
        { name: "8+", count: 32, share: 17.7 },
      ],
      booths: [
        {
          id: "booth-qazaq-it",
          name: "Qazaq IT Community Hub",
          category: "Community & Mentorship",
          location: "Зал A · Стенд A1",
          tags: ["python", "react", "typescript", "community"],
          matching_participants: 142,
        },
        {
          id: "booth-aiid-lab",
          name: "AIID Smart Business & AI Lab",
          category: "AI & Applied Research",
          location: "Зал A · Стенд A2",
          tags: ["artificial intelligence", "machine learning", "data science", "python"],
          matching_participants: 118,
        },
        {
          id: "booth-talent-arena",
          name: "Tech Talent & Career Zone",
          category: "Hiring & Career",
          location: "Зал B · Стенд B1",
          tags: ["frontend", "backend", "react", "typescript"],
          matching_participants: 134,
        },
      ],
    };
  },
  async getProfile() {
    await delay();
    return structuredClone(profile);
  },
  async updateProfile(p: Partial<ProfileMe>) {
    await delay();
    profile = { ...profile, ...p };
    return structuredClone(profile);
  },
  async linkTelegram(): Promise<never> {
    throw new ApiError(501, "not implemented");
  },
};
export function clearMockSession() {
  profile = {};
  feedback.clear();
}
