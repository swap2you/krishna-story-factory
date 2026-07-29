import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { getStories } from "@/lib/catalog";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Printables",
  description: "Download story posters, coloring pages, and activity sheets. Planned learning printables stay honestly marked until reviewed.",
};

const LIVE_TYPES = [
  { id: "poster", label: "Story posters", file: "story_poster.png" },
  { id: "simple", label: "Simple coloring", file: "simple_coloring_page.png" },
  { id: "detailed", label: "Detailed coloring", file: "coloring_page.png" },
  { id: "activity", label: "Activity sheets", file: "activity_sheet.pdf" },
] as const;

const PLANNED = [
  "Word search",
  "Crossword",
  "Word Sudoku",
  "Connect the dots",
  "Sequencing",
  "Matching",
  "Maze",
  "Memory cards",
  "Śloka cards",
  "Teacher packs",
  "Parent guides",
];

export default async function PrintablesPage() {
  const stories = await getStories();

  return (
    <>
      <PageIntro
        eyebrow="Printables"
        title="Devotional learning sheets for home and class."
        body="Live assets come from released story packages. Planned printable types stay empty until curated."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <nav aria-label="Breadcrumb" style={{ marginBottom: "1rem" }}>
            <span className="hint" style={{ fontSize: ".82rem" }}>
              <Link href="/">Home</Link> / <span aria-current="page">Printables</span>
            </span>
          </nav>

          <h2 className="section-heading">Live package assets</h2>
          {!stories.length ? (
            <p className="hint">No catalog stories available yet.</p>
          ) : (
            <div className="scope-grid">
              {stories.map((story) => (
                <article key={story.story_no} className="scope-card">
                  <h3 style={{ marginTop: 0 }}>#{story.story_no} · {story.title}</h3>
                  <ul style={{ paddingLeft: "1.1rem", margin: "0.75rem 0 0" }}>
                    {LIVE_TYPES.map((type) => (
                      <li key={type.id} style={{ marginBottom: "0.35rem" }}>
                        <a href={`/api/v1/stories/${story.story_no}/assets/${type.file}`}>
                          {type.label}
                        </a>
                      </li>
                    ))}
                  </ul>
                  <p className="hint" style={{ marginTop: "0.75rem" }}>
                    <Link href={`/stories/${story.story_no}`}>Open story</Link>
                  </p>
                </article>
              ))}
            </div>
          )}

          <h2 className="section-heading" style={{ marginTop: "2rem" }}>Planned printable types</h2>
          <div className="scope-grid">
            {PLANNED.map((name) => (
              <article key={name} className="scope-card">
                <h3 style={{ marginTop: 0 }}>{name}</h3>
                <p className="hint">Honest planned state — no fabricated worksheet content.</p>
                <span className="editorial-status planned">Planned</span>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
