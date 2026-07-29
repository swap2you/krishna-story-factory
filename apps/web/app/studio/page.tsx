"use client";

import { useEffect, useState } from "react";
import { Button } from "@bhava/ui";
import { PageIntro } from "@/components/page-intro";

type Status = {
  loopback_only?: boolean;
  factory_actions_enabled?: boolean;
  csrf_token?: string;
};

type StorySummary = {
  story_no: string;
  title: string;
};

type EnrichmentStatuses = {
  reader?: string;
  narration?: string;
  reflections?: string;
  shlokas?: string;
  sync?: string;
  source_links?: string;
};

type EnrichmentRow = {
  story_no: string;
  title: string;
  statuses: EnrichmentStatuses | null;
  error?: string;
};

export default function StudioPage() {
  const [status, setStatus] = useState<Status | null>(null);
  const [queue, setQueue] = useState<unknown>(null);
  const [enrichment, setEnrichment] = useState<EnrichmentRow[]>([]);
  const [message, setMessage] = useState("Studio loads only against 127.0.0.1.");

  async function loadEnrichment() {
    try {
      const storiesRes = await fetch("/api/v1/stories");
      if (!storiesRes.ok) {
        setEnrichment([]);
        return;
      }
      const stories = (await storiesRes.json()) as StorySummary[];
      const rows = await Promise.all(
        stories.map(async (story) => {
          try {
            const res = await fetch(`/api/v1/stories/${story.story_no}/web-manifest`);
            if (!res.ok) {
              return {
                story_no: story.story_no,
                title: story.title,
                statuses: null,
                error: `HTTP ${res.status}`,
              } satisfies EnrichmentRow;
            }
            const payload = (await res.json()) as { statuses?: EnrichmentStatuses };
            return {
              story_no: story.story_no,
              title: story.title,
              statuses: payload.statuses ?? null,
            } satisfies EnrichmentRow;
          } catch {
            return {
              story_no: story.story_no,
              title: story.title,
              statuses: null,
              error: "unreachable",
            } satisfies EnrichmentRow;
          }
        }),
      );
      setEnrichment(rows);
    } catch {
      setEnrichment([]);
    }
  }

  async function refresh() {
    try {
      const [statusRes, queueRes] = await Promise.all([
        fetch("/api/v1/local/status"),
        fetch("/api/v1/local/queue"),
      ]);
      setStatus(statusRes.ok ? await statusRes.json() : null);
      setQueue(queueRes.ok ? await queueRes.json() : null);
      setMessage(statusRes.ok ? "Connected to local factory gateway." : "API not reachable on loopback.");
      await loadEnrichment();
    } catch {
      setMessage("API not reachable on loopback.");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const enabled = Boolean(status?.factory_actions_enabled);

  async function post(path: string) {
    if (!enabled || !status?.csrf_token) {
      setMessage(
        "Production actions are disabled (demo mode). Set BHAVA_FACTORY_ACTIONS_ENABLED=true only for intentional local ops.",
      );
      return;
    }
    try {
      const response = await fetch(`/api/v1/local/${path}`, {
        method: "POST",
        headers: {
          "X-Bhava-CSRF-Token": status.csrf_token,
        },
      });
      const payload = (await response.json().catch(() => null)) as {
        operation?: string;
        status?: string;
        detail?: string;
      } | null;
      if (payload && (payload.detail || payload.status || payload.operation)) {
        const parts = [
          payload.operation ? `Operation: ${payload.operation}` : null,
          payload.status ? `Status: ${payload.status}` : null,
          payload.detail ?? null,
        ].filter(Boolean);
        setMessage(parts.join(" · "));
        if (path.startsWith("rebuild-web-assets/")) {
          await loadEnrichment();
        }
        return;
      }
      setMessage(response.ok ? "Action completed." : `Action failed (${response.status}).`);
    } catch {
      setMessage("Could not reach the local factory gateway.");
    }
  }

  return (
    <>
      <div className="local-banner">Local Factory Studio — loopback only · never expose publicly</div>
      <PageIntro
        eyebrow="Factory Studio"
        title="Safe operator console around the locked story factory."
        body="Read queue and health here. Generation buttons stay disabled unless you explicitly enable the local actions flag. This branch must not trigger Story 008."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container studio-stack">
          <section className="studio-panel">
            <h2>Overview</h2>
            <p>{message}</p>
            <p>
              <strong>Actions enabled:</strong> {enabled ? "YES" : "NO (demo)"}
            </p>
            <p>
              <strong>Loopback enforced:</strong> {String(status?.loopback_only ?? "unknown")}
            </p>
            <div className="actions" style={{ marginTop: "1rem" }}>
              <Button onClick={() => void refresh()}>Refresh</Button>
            </div>
          </section>
          <section className="studio-panel">
            <h2>Queue</h2>
            <pre tabIndex={0} aria-label="Factory queue JSON">{JSON.stringify(queue, null, 2)}</pre>
          </section>
          <section className="studio-panel">
            <h2>Web-asset enrichment</h2>
            <p className="hint">
              Read-only status from <code>/api/v1/stories/&lt;n&gt;/web-manifest</code>. Rebuild stays
              disabled unless <code>BHAVA_FACTORY_ACTIONS_ENABLED=true</code>.
            </p>
            {enrichment.length === 0 ? (
              <p className="hint">No catalog stories loaded yet.</p>
            ) : (
              <div className="studio-enrichment-list" style={{ marginTop: "1rem" }}>
                {enrichment.map((row) => (
                  <div
                    key={row.story_no}
                    style={{
                      display: "grid",
                      gap: "0.35rem",
                      padding: "0.85rem 0",
                      borderBottom: "1px solid rgba(6, 22, 40, 0.08)",
                    }}
                  >
                    <strong>
                      {row.story_no} — {row.title}
                    </strong>
                    {row.statuses ? (
                      <p className="hint" style={{ margin: 0 }}>
                        reader: {row.statuses.reader ?? "—"} · sync: {row.statuses.sync ?? "—"} ·
                        shlokas: {row.statuses.shlokas ?? "—"} · reflections:{" "}
                        {row.statuses.reflections ?? "—"}
                      </p>
                    ) : (
                      <p className="hint" style={{ margin: 0 }}>
                        Enrichment unavailable{row.error ? ` (${row.error})` : ""}.
                      </p>
                    )}
                    <div className="actions">
                      <Button
                        variant="quiet"
                        disabled={!enabled}
                        onClick={() => void post(`rebuild-web-assets/${row.story_no}`)}
                      >
                        Rebuild web assets
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
          <section className="studio-panel">
            <h2>Allowlisted operations</h2>
            <div className="actions">
              <Button variant="quiet" disabled={!enabled} onClick={() => void post("preflight")}>
                Preflight
              </Button>
              <Button variant="quiet" disabled={!enabled} onClick={() => void post("generate-next")}>
                Generate next
              </Button>
              <Button variant="quiet" disabled={!enabled} onClick={() => void post("drive/readback")}>
                Drive readback
              </Button>
            </div>
            <p className="hint" style={{ marginTop: "1rem" }}>
              Disabled controls are intentional. Tests and default local runs never call paid providers.
            </p>
          </section>
        </div>
      </section>
    </>
  );
}
