import type { Metadata } from "next";
import Link from "next/link";
import { cookies, headers } from "next/headers";
import { notFound } from "next/navigation";
import { PageIntro } from "@/components/page-intro";
import { getRoadmapCounts, listRoadmap, listRoadmapPillars } from "@/lib/knowledge/loader";
import { listKnowledgePackages } from "@/lib/knowledge/packages";
import { getDraftFactoryStatus } from "@/lib/knowledge/draft-factory";
import { getSourceIntakeSummary, listSourceIntakeItems } from "@/lib/knowledge/source-intake";
import { isLoopbackRequest, isStudioAuthed } from "@/lib/knowledge/studio-guard";
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
  searchParams: Promise<{ q?: string; lifecycle?: string; pillar?: string; page?: string }>;
}) {
  const params = await searchParams;
  const jar = await cookies();
  const hdrs = await headers();
  if (!isLoopbackRequest(hdrs)) {
    notFound();
  }
  const role = jar.get("bhava_studio_role")?.value || "";
  const authed = isStudioAuthed(jar);

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

  const pageSize = 50;
  const page = Math.max(1, Number.parseInt(params.page || "1", 10) || 1);
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const start = (safePage - 1) * pageSize;
  const pageRows = rows.slice(start, start + pageSize);
  const packages = listKnowledgePackages();
  const intakeSummary = getSourceIntakeSummary();
  const intakeItems = listSourceIntakeItems();
  const factoryStatus = getDraftFactoryStatus();

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
                Showing {start + 1}–{Math.min(start + pageSize, rows.length)} of {rows.length} filtered
                (roadmap total {counts.total}). Research/backlog rows are not public until approved.
                Workflow: {WORKFLOW.join(" → ")}.
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
                    {pageRows.map((row) => (
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
              <nav className="knowledge-pager" aria-label="Roadmap pages" style={{ marginTop: "1rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                {safePage > 1 ? (
                  <Link className="bhava-button" href={`?${new URLSearchParams({ ...(params.q ? { q: params.q } : {}), ...(params.lifecycle ? { lifecycle: params.lifecycle } : {}), ...(params.pillar ? { pillar: params.pillar } : {}), page: String(safePage - 1) }).toString()}`}>
                    Previous
                  </Link>
                ) : null}
                <span className="hint">Page {safePage} of {totalPages}</span>
                {safePage < totalPages ? (
                  <Link className="bhava-button" href={`?${new URLSearchParams({ ...(params.q ? { q: params.q } : {}), ...(params.lifecycle ? { lifecycle: params.lifecycle } : {}), ...(params.pillar ? { pillar: params.pillar } : {}), page: String(safePage + 1) }).toString()}`}>
                    Next
                  </Link>
                ) : null}
              </nav>

              <h2 style={{ marginTop: "2rem" }}>Draft factory (read-only)</h2>
              <p className="hint">
                Private 50-item draft factory progress. Zero approve/merge/deploy/publication authority.
              </p>
              {factoryStatus.available ? (
                <div className="scope-grid" style={{ marginTop: "0.75rem" }}>
                  <article className="scope-card">
                    <h3 style={{ marginTop: 0 }}>Run</h3>
                    <p style={{ margin: 0 }}><code>{factoryStatus.run_id}</code></p>
                    <p className="hint">{factoryStatus.dry_run ? "dry-run" : "live-scaffold"} · v{factoryStatus.factory_version}</p>
                  </article>
                  <article className="scope-card">
                    <h3 style={{ marginTop: 0 }}>Queue</h3>
                    <p style={{ fontSize: "1.6rem", margin: 0 }}>{factoryStatus.queue_size ?? 0}</p>
                    <p className="hint">{factoryStatus.items_done ?? 0} done · {factoryStatus.items_blocked_or_duplicate ?? 0} blocked/dup</p>
                  </article>
                  <article className="scope-card">
                    <h3 style={{ marginTop: 0 }}>Idempotency keys</h3>
                    <p style={{ fontSize: "1.6rem", margin: 0 }}>{factoryStatus.completed_keys ?? 0}</p>
                    <p className="hint">Stages completed (resumable)</p>
                  </article>
                  <article className="scope-card">
                    <h3 style={{ marginTop: 0 }}>Authority</h3>
                    <p style={{ margin: 0 }}>approve/merge/deploy/publish = false</p>
                    <p className="hint">{factoryStatus.message}</p>
                  </article>
                </div>
              ) : (
                <p className="hint" style={{ marginTop: "0.75rem" }}>{factoryStatus.message}</p>
              )}

              <h2 style={{ marginTop: "2rem" }}>Source intake (private metadata)</h2>
              <p className="hint">
                Owner-PDF inventory only — no PDF bytes, no public serving.
                {" "}{intakeSummary.total} staged
                {" · "}{intakeSummary.by_status.STAGED_SOURCE_CANDIDATE || 0} STAGED_SOURCE_CANDIDATE
                {" · "}{intakeSummary.ocr_pending} OCR_PENDING
                {" · "}dossier_ready {intakeSummary.dossier_ready}
                {" · "}public_allowed {intakeSummary.public_allowed}.
              </p>
              {intakeItems.length ? (
                <div style={{ overflowX: "auto", marginTop: "0.75rem" }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Original</th>
                        <th>Status</th>
                        <th>OCR</th>
                        <th>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {intakeItems.map((item) => (
                        <tr key={item.sequence}>
                          <td>{item.sequence}</td>
                          <td><code>{item.original_filename}</code></td>
                          <td>{item.status}</td>
                          <td>{item.ocr_state}</td>
                          <td>{item.notes}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="hint">Intake ledger not found.</p>
              )}

              <h2 style={{ marginTop: "2rem" }}>Knowledge packages (private)</h2>
              <p className="hint">
                Pilot packages for loopback preview. Production scripture stays blocked until dossier approval.
              </p>
              <ul>
                {packages.map((pkg) => (
                  <li key={pkg.record.record_id}>
                    <Link href={`/studio/knowledge/preview/${pkg.record.slug}`}>
                      {pkg.record.title}
                    </Link>
                    {" · "}
                    <strong>{pkg.record.source_status}</strong>
                    {pkg.record.fixture ? ` · ${pkg.record.fixture_label}` : null}
                  </li>
                ))}
              </ul>
              <p className="hint" style={{ marginTop: "1.5rem" }}>
                This foundation provides a read-only roadmap/package queue, authenticated
                loopback private preview, and synthetic study-neutral PDF/DOCX exports.
                Create/edit mutations, reviewer workflows, scheduling, and publication actions
                are not implemented in P01C.
              </p>
              <p><Link href="/knowledge">Public Knowledge home</Link></p>
            </>
          )}
        </div>
      </section>
    </>
  );
}
