import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CalendarClock, MapPin, Sparkles } from "lucide-react";
import { useMatches } from "../hooks/useMatches";
import { CONFERENCE_SLOTS } from "../contexts/MatchesContext";
import { useOnboardingDraft } from "../hooks/useOnboardingDraft";
import { useI18n } from "../hooks/useI18n";
import { validDraft } from "../lib/validation";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { EmptyState } from "../components/EmptyState";
import { MatchCard } from "../components/MatchCard";
import { DemoBanner } from "../components/DemoBanner";
import { Button } from "../components/ui/Button";
export default function Matches() {
  const m = useMatches(),
    { draft } = useOnboardingDraft(),
    { t } = useI18n(),
    navigate = useNavigate();
  useEffect(() => {
    if (m.status === "idle") {
      if (validDraft(draft)) void m.fetchMatches(draft);
      else navigate("/onboarding", { replace: true });
    }
  }, [m.status]);
  return (
    <section className="page container">
      <div className="page-heading">
        <span className="eyebrow">MeetMatch AI</span>
        <h1>{t("matches.title")}</h1>
        {m.processingMs !== undefined && m.status !== "loading" && (
          <p className="muted">
            {t("matches.processing", { ms: m.processingMs })}
          </p>
        )}
      </div>
      {m.isDemo && <DemoBanner reason="api" />}
      {m.status === "loading" || m.status === "idle" ? (
        <LoadingState variant="matches" />
      ) : m.status === "error" ? (
        <>
          <ErrorState
            message={t(m.error?.message ?? "errors.generic")}
            onRetry={() => void m.fetchMatches(draft)}
            actions={
              <Link className="btn btn-secondary" to="/onboarding">
                {t("matches.edit")}
              </Link>
            }
          />
          {m.error?.status === 422 && Array.isArray(m.error.detail) && (
            <ul className="error-text">
              {m.error.detail.map((item, i) => {
                const field = Array.isArray(item.loc)
                  ? item.loc.find((k: string) =>
                      [
                        "role",
                        "stack",
                        "experience",
                        "interests",
                        "about",
                        "goal",
                      ].includes(k),
                    )
                  : null;
                return field ? (
                  <li key={i}>
                    {t(`field.${field}`)}: {t(`validation.${field}`)}
                  </li>
                ) : null;
              })}
            </ul>
          )}
        </>
      ) : m.status === "empty" ? (
        <EmptyState />
      ) : (
        <>
          <div className="card slot-filter-bar">
            <div className="slot-filter-title">
              <CalendarClock size={18} className="text-accent" />
              <div>
                <strong>{t("matches.slots.filterTitle")}</strong>
                <p className="hint">{t("matches.slots.filterHint")}</p>
              </div>
            </div>
            <div className="slot-pills">
              {CONFERENCE_SLOTS.map((slot) => {
                const active = m.preferredSlots.includes(slot);
                return (
                  <button
                    key={slot}
                    type="button"
                    className={`slot-pill ${active ? "mutual" : ""}`}
                    aria-pressed={active}
                    onClick={() => m.togglePreferredSlot(slot)}
                  >
                    {slot}
                  </button>
                );
              })}
            </div>
          </div>
          {m.status === "partial" && (
            <p className="notice" role="status">
              {t("matches.partial", { count: m.matches.length })}
            </p>
          )}
          {m.rejected && (
            <div className="notice actions" role="status">
              {t("matches.refreshPrompt")}
              <Button
                variant="secondary"
                onClick={() => void m.fetchMatches(draft)}
              >
                {t("matches.refresh")}
              </Button>
            </div>
          )}
          <div className="match-grid">
            {m.matches.map((match, i) => (
              <MatchCard
                key={match.id}
                match={match}
                index={i}
                status={m.cards[match.id] ?? "idle"}
                onFeedback={m.sendFeedback}
                preferredSlots={m.preferredSlots}
                scheduledSlot={m.scheduledSlots[match.id] ?? ""}
                onScheduleSlot={m.scheduleSlot}
              />
            ))}
          </div>
          {m.booths.length > 0 && (
            <div className="booths-section">
              <div className="section-heading">
                <span className="eyebrow">
                  <Sparkles size={14} /> {t("matches.booths.eyebrow")}
                </span>
                <h2>{t("matches.booths.title")}</h2>
                <p className="muted">{t("matches.booths.subtitle")}</p>
              </div>
              <div className="three-grid">
                {m.booths.map((booth) => (
                  <article key={booth.id} className="card booth-card">
                    <div className="booth-head">
                      <span className="badge">{booth.category}</span>
                      <span className="booth-score">{booth.match_score}%</span>
                    </div>
                    <h3>{booth.name}</h3>
                    <p className="booth-location muted">
                      <MapPin size={15} /> {booth.location}
                    </p>
                    <p className="booth-reason">{booth.reason}</p>
                    <div className="tags">
                      {booth.tags.map((tag) => (
                        <span key={tag} className="badge">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}
        </>
      )}
      {!["loading", "idle"].includes(m.status) && (
        <div className="actions mt-8">
          <Button onClick={() => void m.fetchMatches(draft)}>
            {t("matches.refresh")}
          </Button>
          <Link className="btn btn-secondary" to="/onboarding">
            {t("matches.edit")}
          </Link>
          <Link className="btn btn-secondary" to="/organizer">
            {t("nav.organizer")}
          </Link>
        </div>
      )}
    </section>
  );
}
