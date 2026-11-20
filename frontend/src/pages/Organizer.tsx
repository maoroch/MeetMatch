import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, Building2, Sparkles, ThumbsUp, UsersRound } from "lucide-react";
import { api, ApiError } from "../services/api";
import { useI18n } from "../hooks/useI18n";
import type { OrganizerStats } from "../types";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";

export default function Organizer() {
  const { t } = useI18n(),
    [stats, setStats] = useState<OrganizerStats | null>(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api
      .organizerStats()
      .then((res) => {
        if (active) setStats(res);
      })
      .catch((e) => {
        if (active) setError(e instanceof ApiError ? e.message : "errors.generic");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [retry]);

  return (
    <section className="page container">
      <div className="page-heading">
        <span className="eyebrow">
          <BarChart3 size={14} /> {t("organizer.eyebrow")}
        </span>
        <h1>{t("organizer.title")}</h1>
        <p className="muted">{t("organizer.subtitle")}</p>
      </div>

      {loading ? (
        <LoadingState />
      ) : error || !stats ? (
        <ErrorState
          message={t(error || "errors.generic")}
          onRetry={() => setRetry((n) => n + 1)}
        />
      ) : (
        <div className="organizer-grid">
          <div className="organizer-kpi-grid">
            <div className="card kpi-card">
              <div className="feature-icon">
                <UsersRound size={22} />
              </div>
              <div>
                <strong>{stats.total_participants}</strong>
                <p className="muted">{t("organizer.kpi.participants")}</p>
              </div>
            </div>
            <div className="card kpi-card">
              <div className="feature-icon">
                <Sparkles size={22} />
              </div>
              <div>
                <strong>{stats.top_skills.length + stats.top_interests.length}</strong>
                <p className="muted">{t("organizer.kpi.clusters")}</p>
              </div>
            </div>
            <div className="card kpi-card">
              <div className="feature-icon">
                <ThumbsUp size={22} />
              </div>
              <div>
                <strong>{stats.total_feedback}</strong>
                <p className="muted">{t("organizer.kpi.feedback")}</p>
              </div>
            </div>
            <div className="card kpi-card">
              <div className="feature-icon">
                <Building2 size={22} />
              </div>
              <div>
                <strong>{stats.booths.length}</strong>
                <p className="muted">{t("organizer.kpi.booths")}</p>
              </div>
            </div>
          </div>

          <div className="two-grid">
            <article className="card form-card">
              <h2>{t("organizer.goals.title")}</h2>
              <div className="stat-bars">
                {stats.goals.map((g) => {
                  const goalKey =
                    g.goal === "offer_mentorship"
                      ? "be_mentor"
                      : g.goal === "find_investor"
                        ? "exchange_experience"
                        : g.goal;
                  const label = t(`goals.${goalKey}.title`);
                  return (
                    <div key={g.goal} className="stat-bar-row">
                      <div className="stat-bar-label">
                        <span>{label}</span>
                        <span className="muted">
                          {g.count} ({g.share}%)
                        </span>
                      </div>
                      <progress
                        max={100}
                        value={g.share}
                        aria-label={`${label}: ${g.share}%`}
                      />
                    </div>
                  );
                })}
              </div>
            </article>

            <article className="card form-card">
              <h2>{t("organizer.experience.title")}</h2>
              <div className="stat-bars">
                {stats.experience_buckets.map((b) => (
                  <div key={b.name} className="stat-bar-row">
                    <div className="stat-bar-label">
                      <span>
                        {b.name} {t("organizer.experience.years")}
                      </span>
                      <span className="muted">
                        {b.count} ({b.share}%)
                      </span>
                    </div>
                    <progress
                      max={100}
                      value={b.share}
                      aria-label={`${b.name}: ${b.share}%`}
                    />
                  </div>
                ))}
              </div>
            </article>
          </div>

          <div className="two-grid">
            <article className="card form-card">
              <h2>{t("organizer.skills.title")}</h2>
              <div className="tags">
                {stats.top_skills.map((s) => (
                  <span key={s.name} className="tag">
                    <strong>{s.name}</strong>
                    <span className="muted">
                      {s.count} · {s.share}%
                    </span>
                  </span>
                ))}
              </div>
            </article>

            <article className="card form-card">
              <h2>{t("organizer.interests.title")}</h2>
              <div className="tags">
                {stats.top_interests.map((item) => (
                  <span key={item.name} className="tag">
                    <strong>{item.name}</strong>
                    <span className="muted">
                      {item.count} · {item.share}%
                    </span>
                  </span>
                ))}
              </div>
            </article>
          </div>

          <article className="card form-card">
            <h2>{t("organizer.booths.title")}</h2>
            <div
              tabIndex={0}
              role="region"
              aria-labelledby="organizer-booths-caption"
              className="table-wrapper"
            >
              <table
                className="organizer-table"
                style={
                  {
                    "--label-1": `"${t("organizer.table.booth")}"`,
                    "--label-2": `"${t("organizer.table.category")}"`,
                    "--label-3": `"${t("organizer.table.location")}"`,
                    "--label-4": `"${t("organizer.table.demand")}"`,
                  } as React.CSSProperties
                }
              >
                <caption id="organizer-booths-caption" className="sr-only">
                  {t("organizer.booths.title")}
                </caption>
                <thead>
                  <tr>
                    <th scope="col">{t("organizer.table.booth")}</th>
                    <th scope="col">{t("organizer.table.category")}</th>
                    <th scope="col">{t("organizer.table.location")}</th>
                    <th scope="col">{t("organizer.table.demand")}</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.booths.map((b) => (
                    <tr key={b.id}>
                      <th scope="row">{b.name}</th>
                      <td>{b.category}</td>
                      <td>{b.location}</td>
                      <td>
                        <strong>{b.matching_participants}</strong>{" "}
                        <span className="muted">
                          ({Math.round((b.matching_participants * 100) / Math.max(1, stats.total_participants))}%)
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <div className="actions">
            <Link className="btn btn-primary" to="/onboarding">
              {t("home.hero.cta")}
            </Link>
            <Link className="btn btn-secondary" to="/">
              {t("common.home")}
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}
