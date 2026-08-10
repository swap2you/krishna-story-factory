import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import {
  listPublicPilotCatalog,
  listPathways,
} from "@/lib/knowledge/loader";
import { brandSrc } from "@/lib/brand-assets";

export const metadata: Metadata = {
  title: "Bhāva Knowledge Library",
  description:
    "Public Knowledge pilot — Bhāva-original guides and FAQs for families and teachers. No fabricated scripture pages.",
};

type Props = {
  searchParams: Promise<{ kind?: string }>;
};

const REAL_TOOLS: { href: string; label: string; body: string }[] = [
  {
    href: "/knowledge/search",
    label: "Search",
    body: "Search approved public guides and FAQs only.",
  },
  {
    href: "/knowledge/ask",
    label: "Ask privately",
    body: "Private intake — not an open forum.",
  },
  {
    href: "/knowledge/corrections",
    label: "Suggest a correction",
    body: "Request a fix on a published record.",
  },
  {
    href: "/knowledge/standards",
    label: "Editorial standards",
    body: "How Bhāva reviews and publishes Knowledge.",
  },
];

export default async function KnowledgeHomePage({ searchParams }: Props) {
  const { kind: kindRaw } = await searchParams;
  const kind =
    kindRaw === "guides" || kindRaw === "questions" ? kindRaw : "all";
  const { guides, questions, total } = listPublicPilotCatalog();
  const pathways = listPathways();
  const publishedPathways = pathways.filter((p) => p.status === "published");
  const plannedPathways = pathways.filter((p) => p.status !== "published");

  const showGuides = kind === "all" || kind === "guides";
  const showQuestions = kind === "all" || kind === "questions";

  return (
    <>
      <PageIntro
        eyebrow="Knowledge"
        title="Bhāva Knowledge Library"
        body="A public pilot of Bhāva-original guides and FAQs — source-honest study for families and teachers, not a random blog or open forum. Scripture packages stay blocked until editions and rights clear."
        heroSrc={brandSrc("collection-bhakti-blog")}
      />
      <section className="section">
        <div className="container knowledge-home">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Public pilot · Available</h3>
              <p>
                {total} published record{total === 1 ? "" : "s"}: {guides.length}{" "}
                guide{guides.length === 1 ? "" : "s"} and {questions.length}{" "}
                canonical question{questions.length === 1 ? "" : "s"}. All are
                labeled Bhāva-original — no scripture bodies from TOP-0147 or
                intake PDFs.
              </p>
            </article>
            <article className="scope-card">
              <h3>Still planned / blocked</h3>
              <p>
                Pathway shells ({plannedPathways.length} planned) and private
                dossiers stay out of this catalog as clickable shelves. Golden
                scripture work remains blocked until source adequacy clears.
                Editorial queues live in Studio — not here.
              </p>
            </article>
          </div>

          <form className="search-bar" action="/knowledge/search" method="get">
            <label className="sr-only" htmlFor="knowledge-search">
              Search Knowledge
            </label>
            <input
              id="knowledge-search"
              name="q"
              placeholder="Search approved public guides and FAQs"
            />
            <button className="bhava-button bhava-button--primary" type="submit">
              Search
            </button>
          </form>

          <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>
            Public pilot collection
          </h2>
          <p className="section-lead">
            Filters cover only content that exists today. Empty shelves are not
            shown as Available.
          </p>

          <nav className="knowledge-pilot-filters" aria-label="Pilot filters">
            <Link href="/knowledge" aria-current={kind === "all" ? "page" : undefined}>
              All ({total})
            </Link>
            <Link
              href="/knowledge?kind=guides"
              aria-current={kind === "guides" ? "page" : undefined}
            >
              Guides ({guides.length})
            </Link>
            <Link
              href="/knowledge?kind=questions"
              aria-current={kind === "questions" ? "page" : undefined}
            >
              Q&amp;A ({questions.length})
            </Link>
          </nav>

          {showGuides ? (
            <>
              <h3 className="section-heading" style={{ marginTop: "1.75rem", fontSize: "1.15rem" }}>
                Guides
              </h3>
              {guides.length ? (
                <div className="scope-grid">
                  {guides.map((a) => (
                    <article key={a.slug} className="scope-card">
                      <h3 style={{ marginTop: 0 }}>
                        <Link href={`/knowledge/${a.slug}`}>{a.title}</Link>
                      </h3>
                      <p style={{ marginBottom: ".65rem" }}>{a.summary}</p>
                      <p className="hint" style={{ marginBottom: ".65rem" }}>
                        Bhāva-original · {a.review_state}
                      </p>
                      <span className="editorial-status active">Available</span>
                    </article>
                  ))}
                </div>
              ) : (
                <p className="hint">No guides match this filter.</p>
              )}
            </>
          ) : null}

          {showQuestions ? (
            <>
              <h3 className="section-heading" style={{ marginTop: "1.75rem", fontSize: "1.15rem" }}>
                Canonical questions
              </h3>
              {questions.length ? (
                <div className="scope-grid">
                  {questions.map((q) => (
                    <article key={q.slug} className="scope-card">
                      <h3 style={{ marginTop: 0 }}>
                        <Link href={`/knowledge/questions/${q.slug}`}>{q.title}</Link>
                      </h3>
                      <p style={{ marginBottom: ".65rem" }}>{q.summary}</p>
                      <p className="hint" style={{ marginBottom: ".65rem" }}>
                        Bhāva-original · {q.review_state}
                      </p>
                      <span className="editorial-status active">Available</span>
                    </article>
                  ))}
                </div>
              ) : (
                <p className="hint">No questions match this filter.</p>
              )}
            </>
          ) : null}

          <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>
            Tools that exist
          </h2>
          <ul className="plain-list">
            {REAL_TOOLS.map((tool) => (
              <li key={tool.href}>
                <Link href={tool.href}>{tool.label}</Link>
                <span className="hint"> — {tool.body}</span>
              </li>
            ))}
            <li>
              <Link href="/teachers">Teachers</Link>
              <span className="hint"> — classroom playlist helper</span>
            </li>
            <li>
              <Link href="/sunday-school">Sunday School</Link>
              <span className="hint"> — weekly planner</span>
            </li>
            <li>
              <Link href="/learning">Learning hub</Link>
              <span className="hint"> — pathways and public derivatives</span>
            </li>
          </ul>

          {publishedPathways.length ? (
            <>
              <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>
                Published pathway labels
              </h2>
              <p className="hint" style={{ marginBottom: "1rem" }}>
                These labels already have related public pilot records. They are
                orientation links, not empty shelves.
              </p>
              <ul className="plain-list">
                {publishedPathways.map((p) => (
                  <li key={p.slug}>
                    <Link href={`/knowledge/pathways/${p.slug}`}>{p.title}</Link>
                    <span className="editorial-status active" style={{ marginLeft: ".5rem" }}>
                      Available
                    </span>
                  </li>
                ))}
              </ul>
            </>
          ) : null}

          {plannedPathways.length ? (
            <>
              <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>
                Planned pathway shells
              </h2>
              <p className="hint" style={{ marginBottom: "1rem" }}>
                Named honestly and not offered as finished reading shelves.
              </p>
              <ul className="plain-list">
                {plannedPathways.map((p) => (
                  <li key={p.slug}>
                    <span>{p.title}</span>
                    <span className="editorial-status planned" style={{ marginLeft: ".5rem" }}>
                      Planned
                    </span>
                  </li>
                ))}
              </ul>
            </>
          ) : null}

          <aside className="knowledge-roadmap-note" style={{ marginTop: "2.5rem" }}>
            <h2 className="section-heading">How publishing works</h2>
            <p className="hint">
              Only approved and published Bhāva-original resources appear here.
              TOP-0147 and the twelve intake PDFs remain source-blocked. Private
              editorial counts live in the local studio — never as a public
              “finished content” claim.
            </p>
          </aside>
        </div>
      </section>
    </>
  );
}
