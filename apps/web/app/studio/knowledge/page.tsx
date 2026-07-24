import type { Metadata } from "next";
import Link from "next/link";
import { cookies } from "next/headers";
import { PageIntro } from "@/components/page-intro";
import { getRoadmapCounts, listRoadmap, listRoadmapPillars } from "@/lib/knowledge/loader";
import { StudioClient } from "./studio-client";

export const metadata: Metadata = {
  title: "Knowledge editorial studio",
  robots: { index: false, follow: false },
};

const ROLES = [
  "steward",
  "administrator",
  "contributor",
  "content_editor",
  "scriptural_reviewer",
  "devotional_reviewer",
  "copy_editor",
  "moderator",
  "auditor",
] as const;

const WORKFLOW = [
  "Draft",
  "Source Review",
  "Devotional Review",
  "Copy Review",
  "Approved",
  "Scheduled",
  "Published",
  "Updated",
  "Archived",
] as const;

export default async function KnowledgeStudioPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; lifecycle?: string; pillar?: string }>;
}) {
  const params = await searchParams;
  const jar = await cookies();
  const role = jar.get("bhava_studio_role")?.value || "";
  const authed = Boolean(jar.get("bhava_studio_session")?.value) && ROLES.includes(role as (typeof ROLES)[number]);

  const counts = getRoadmapCounts(true);
  const pillars = listRoadmapPillars(true);
  let rows = listRoadmap(true);
  if (params.lifecycle) rows = rows.filter((r) => r.lifecycle === params.lifecycle);
  if (params.pillar) rows = rows.filter((r) => r.pillar === params.pillar);
  if (params.q?.trim()) {
    const q = params.q.trim().toLowerCase();
    rows = rows.filter((r) =>
      [r.id, r.title, r.cluster, r.content_type].join(" ").toLowerCase().includes(q),
    );
  }

  return (
    <>
      <PageIntro
        eyebrow="Local studio"
        title="Knowledge Editorial Studio"
        body="Private publishing workflow for the Bhāva Knowledge Library. Absent from public navigation. Loopback-oriented bootstrap auth — no external IdP required."
      />
      <section className="section">
        <div className="container" style={{ maxWidth: 1100 }}>
          {!authed ? (
            <StudioClient mode="login" roles={[...ROLES]} />
          ) : (
            <>
              <StudioClient mode="session" role={role} roles={[...ROLES]} workflow={[...WORKFLOW]} />
              <div className="scope-grid" style={{ marginTop: "1.5rem" }}>
                <article className="scope-card">
                  <h3 style={{ marginTop: 0 }}>Roadmap total</h3>
                  <p style={{ fontSize: "2rem", margin: 0 }}>{counts.total}</p>
                  <p className="hint">Exact imported governed records</p>
                </article>
                {Object.entries(counts.lifecycle).map(([key, value]) => (
                  <article key={key} className="scope-card">
                    <h3 style={{ marginTop: 0 }}>{key}</h3>
                    <p style={{ fontSize: "1.6rem", margin: 0 }}>{value}</p>
                  </article>
                ))}
              </div>

              <form className="search-bar" style={{ marginTop: "1.5rem" }} method="get">
                <label className="sr-only" htmlFor="studio-q">Filter roadmap</label>
                <input id="studio-q" name="q" defaultValue={params.q || ""} placeholder="Filter by id, title, cluster…" />
                <select name="lifecycle" defaultValue={params.lifecycle || ""} aria-label="Lifecycle">
                  <option value="">All lifecycles</option>
                  {Object.keys(counts.lifecycle).map((key) => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
                <select name="pillar" defaultValue={params.pillar || ""} aria-label="Pillar">
                  <option value="">All pillars</option>
                  {pillars.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
                <button className="bhava-button bhava-button--primary" type="submit">Filter</button>
              </form>

              <p className="hint" style={{ marginTop: "1rem" }}>
                Showing {rows.length} of {counts.total}. Workflow: {WORKFLOW.join(" → ")}.
              </p>

              <div style={{ overflowX: "auto", marginTop: "1rem" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Pillar</th>
                      <th>Type</th>
                      <th>Lifecycle</th>
                      <th>Reviewer</th>
                      <th>Tier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.slice(0, 200).map((row) => (
                      <tr key={row.id}>
                        <td><code>{row.id}</code></td>
                        <td>{row.title}</td>
                        <td>{row.pillar}</td>
                        <td>{row.content_type}</td>
                        <td>{row.lifecycle}</td>
                        <td>{row.required_reviewer}</td>
                        <td>{row.source_tier_required}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {rows.length > 200 ? (
                <p className="hint">First 200 rows shown — refine filters to narrow.</p>
              ) : null}
              <p className="hint" style={{ marginTop: "1.5rem" }}>
                Capabilities: create/edit metadata, Markdown preview, citation/source panel, rights/confidentiality,
                reviewer assignment, comments, revisions, approval/rejection, scheduling, rollback/archive,
                taxonomy, duplicate detection, broken-link review, audit history. Production mutations stay disabled unless factory actions are explicitly enabled.
              </p>
              <p><Link href="/knowledge">Public Knowledge home</Link></p>
            </>
          )}
        </div>
      </section>
    </>
  );
}
