import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { api, ApiError, type MatchResult } from "../services/api";
import { normalizeRequest } from "../lib/validation";
import type {
  MatchRequest,
  MatchesStatus,
  MatchCardStatus,
  FeedbackAction,
} from "../types";

export const CONFERENCE_SLOTS = [
  "11:30–11:45",
  "12:15–12:30",
  "13:30–13:45",
  "14:45–15:00",
  "16:00–16:15",
  "17:00–17:15",
] as const;

function useMatchesState() {
  const [status, setStatus] = useState<MatchesStatus>("idle"),
    [result, setResult] = useState<MatchResult>({ matches: [] }),
    [error, setError] = useState<ApiError | null>(null),
    [cards, setCards] = useState<Record<string, MatchCardStatus>>({}),
    [rejected, setRejected] = useState(false),
    [rejectedIds, setRejectedIds] = useState<string[]>([]),
    [preferredSlots, setPreferredSlots] = useState<string[]>([]),
    [scheduledSlots, setScheduledSlots] = useState<Record<string, string>>({});
  const busy = useRef(false),
    generation = useRef(0),
    sending = useRef(new Set<string>());
  const reset = () => {
    generation.current++;
    busy.current = false;
    sending.current.clear();
    setStatus("idle");
    setResult({ matches: [] });
    setError(null);
    setCards({});
    setRejected(false);
    setRejectedIds([]);
    setPreferredSlots([]);
    setScheduledSlots({});
  };
  useEffect(() => {
    window.addEventListener("meetmatch:reset", reset);
    return () => window.removeEventListener("meetmatch:reset", reset);
  }, []);
  async function fetchMatches(p: MatchRequest, slotsOverride?: string[]) {
    if (busy.current) return;
    busy.current = true;
    const run = ++generation.current;
    setStatus("loading");
    setError(null);
    setCards({});
    setRejected(false);
    sending.current.clear();
    try {
      const normalized = normalizeRequest(p);
      const activeSlots = slotsOverride ?? preferredSlots;
      const r = await api.match({
        ...normalized,
        ...(rejectedIds.length ? { exclude_ids: rejectedIds } : {}),
        ...(activeSlots.length ? { preferred_slots: activeSlots } : {}),
      });
      if (run !== generation.current) return;
      setResult(r);
      setStatus(
        r.matches.length === 0
          ? "empty"
          : r.matches.length < 5
            ? "partial"
            : "success",
      );
    } catch (e) {
      if (run !== generation.current) return;
      setError(e instanceof ApiError ? e : new ApiError(0, "errors.network"));
      setStatus("error");
    } finally {
      if (run === generation.current) busy.current = false;
    }
  }
  async function sendFeedback(id: string, action: FeedbackAction) {
    if (
      sending.current.has(id) ||
      cards[id] === "met" ||
      cards[id] === "rejected"
    )
      return;
    const run = generation.current;
    sending.current.add(id);
    setCards((c) => ({ ...c, [id]: "sending" }));
    try {
      await api.feedback({ match_id: id, action });
      if (run !== generation.current) return;
      setCards((c) => ({ ...c, [id]: action === "met" ? "met" : "rejected" }));
      if (action === "not_fit") {
        setRejected(true);
        setRejectedIds((prev) => (prev.includes(id) ? prev : [...prev, id]));
      }
    } catch (e) {
      if (run === generation.current) setCards((c) => ({ ...c, [id]: "idle" }));
      throw e;
    } finally {
      sending.current.delete(id);
    }
  }
  function togglePreferredSlot(slot: string) {
    setPreferredSlots((prev) =>
      prev.includes(slot) ? prev.filter((s) => s !== slot) : [...prev, slot],
    );
  }
  function scheduleSlot(matchId: string, slot: string) {
    setScheduledSlots((prev) => ({
      ...prev,
      [matchId]: prev[matchId] === slot ? "" : slot,
    }));
  }
  return {
    status,
    matches: result.matches,
    booths: result.recommended_booths ?? [],
    processingMs: result.processing_ms,
    isDemo: result.__demo ?? false,
    error,
    fetchMatches,
    sendFeedback,
    reset,
    cards,
    rejected,
    preferredSlots,
    togglePreferredSlot,
    scheduledSlots,
    scheduleSlot,
  };
}
const Matches = createContext<ReturnType<typeof useMatchesState>>(null!);
export function MatchesProvider({ children }: { children: ReactNode }) {
  return (
    <Matches.Provider value={useMatchesState()}>{children}</Matches.Provider>
  );
}
export const useMatches = () => useContext(Matches);
