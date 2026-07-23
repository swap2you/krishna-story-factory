import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";
import { getStories } from "@/lib/catalog";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "For Preachers",
  description: "Select stories from the catalog, preview source references and outlines, and export materials for preaching programs.",
};

export default async function PreachersPage() {
  const stories = await getStories();
  const hasStories = stories.length > 0;

  return (
    <>
      <PageIntro
        eyebrow="For preachers"
        title="Source-referenced materials for your next program."
        body="Browse released stories, preview outlines and source references, and export printable or text-format handouts — all governed by verified scripture citations."
      />
      <section className="section">
        <div className="container" style={{ maxWidth: 960 }}>
          <section className="teacher-panel">
            <h2>Story selector</h2>
            <p className="hint">
              {hasStories
                ? `${stories.length} stories available from the catalog API. Select a story to preview its source references and outline.`
                : "Start the Bhāva API to load available stories from the catalog. No stories are currently accessible."
              }
            </p>
            {hasStories ? (
              <div className="scope-grid" style={{ marginTop: "1rem" }}>
                {stories.map((story) => (
                  <article key={story.story_no} className="scope-card">
                    <h3 style={{ fontSize: "1.05rem" }}>
                      <span style={{ color: "var(--bhava-saffron)", marginRight: ".4rem" }}>#{story.story_no}</span>
                      {story.title}
                    </h3>
                    {story.source_reference ? (
                      <p style={{ margin: ".35rem 0 0", fontSize: ".88rem" }}>
                        <strong>Source:</strong> {story.source_reference}
                      </p>
                    ) : null}
                    {story.scripture_reference ? (
                      <p style={{ margin: ".25rem 0 0", fontSize: ".88rem" }}>
                        <strong>Scripture:</strong> {story.scripture_reference}
                      </p>
                    ) : null}
                    {story.summary ? (
                      <p style={{ margin: ".5rem 0 0", color: "var(--bhava-muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                        {story.summary}
                      </p>
                    ) : null}
                    <div style={{ marginTop: ".75rem", display: "flex", gap: ".5rem", flexWrap: "wrap" }}>
                      {story.quality_status ? (
                        <span className={`editorial-status ${story.quality_status === "released" ? "active" : "planned"}`}>
                          {story.quality_status}
                        </span>
                      ) : null}
                      {story.age_range ? (
                        <span className="editorial-status planned">{story.age_range}</span>
                      ) : null}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="coming" style={{ minHeight: "20vh" }}>
                <div>
                  <p>Run the local API so the catalog can discover released story packages.</p>
                </div>
              </div>
            )}
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Outline preview</h2>
            <p className="hint">
              When a story is selected above, this section will show a structured outline suitable for
              preaching preparation — story arc, key themes, source verse range, and discussion points.
            </p>
            <div className="source-boundary">
              <p style={{ margin: 0 }}>
                Outlines are generated from the story package <code>manifest.json</code> and <code>story.md</code> content.
                No fabricated quotations or invented teachings will appear here.
              </p>
            </div>
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Export options</h2>
            <p className="hint">Planned export formats for preaching handouts and presentation aids.</p>
            <div className="scope-grid">
              <article className="scope-card">
                <h3>Print handout</h3>
                <p>A printable HTML summary with story outline, source references, and discussion prompts.</p>
                <span className="editorial-status planned" style={{ marginTop: ".5rem" }}>Planned</span>
              </article>
              <article className="scope-card">
                <h3>Text export</h3>
                <p>Plain-text file with story outline and source citations for use in messaging apps or email.</p>
                <span className="editorial-status planned" style={{ marginTop: ".5rem" }}>Planned</span>
              </article>
              <article className="scope-card">
                <h3>Source reference card</h3>
                <p>Compact card listing all scripture references for a story, suitable for quick reference during a talk.</p>
                <span className="editorial-status planned" style={{ marginTop: ".5rem" }}>Planned</span>
              </article>
            </div>
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Source governance</h2>
            <div className="source-boundary">
              <p style={{ margin: 0 }}>
                All preacher materials reference verified scripture citations from story packages.
                No quotations from Śrīla Prabhupāda or other ācāryas are fabricated or paraphrased.
                Source references link directly to the original chapter and verse range.
              </p>
            </div>
          </section>
        </div>
      </section>
    </>
  );
}
