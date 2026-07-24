import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import {
  listArticles,
  listPathways,
  listQuestions,
} from "@/lib/knowledge/loader";
import { brandSrc } from "@/lib/brand-assets";

export const metadata: Metadata = {
  title: "Bhāva Knowledge Library",
  description: "Curated devotional documentation for families, teachers, and preachers — not an open forum.",
};

const GROUPS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: "Learn the foundations",
    links: [
      { href: "/knowledge/pathways/new-to-bhakti", label: "New to Bhakti" },
      { href: "/knowledge/topics", label: "Topics & pathways" },
      { href: "/knowledge/scriptures", label: "Scriptures" },
      { href: "/knowledge/learning-paths", label: "Learning paths" },
    ],
  },
  {
    title: "Practice & worship",
    links: [
      { href: "/knowledge/pathways/daily-practice", label: "Daily Practice" },
      { href: "/knowledge/prayers", label: "Prayers & Āratis" },
      { href: "/knowledge/slokas", label: "Ślokas & Stutis" },
      { href: "/knowledge/pathways/deity-worship", label: "Deity Worship" },
    ],
  },
  {
    title: "Community & service",
    links: [
      { href: "/knowledge/pathways/families-children", label: "Families & Children" },
      { href: "/teachers", label: "Teachers" },
      { href: "/preachers", label: "Preachers" },
      { href: "/sunday-school", label: "Sunday School" },
    ],
  },
  {
    title: "Ask & standards",
    links: [
      { href: "/knowledge/questions", label: "Q&A" },
      { href: "/knowledge/ask", label: "Ask privately" },
      { href: "/knowledge/corrections", label: "Suggest a correction" },
      { href: "/knowledge/standards", label: "Editorial standards" },
      { href: "/knowledge/index", label: "Alphabetical index" },
      { href: "/knowledge/recent", label: "Recently updated" },
    ],
  },
];

export default function KnowledgeHomePage() {
  const pathways = listPathways();
  const articles = listArticles();
  const questions = listQuestions();

  return (
    <>
      <PageIntro
        eyebrow="Knowledge"
        title="Bhāva Knowledge Library"
        body="A curated documentation library for Krishna Book learning, practice pathways, and carefully reviewed Q&A. Public pages show approved resources only; the editorial roadmap stays private until reviewed."
        heroSrc={brandSrc("collection-bhakti-blog")}
      />
      <section className="section">
        <div className="container knowledge-home">
          <form className="search-bar" action="/knowledge/search" method="get">
            <label className="sr-only" htmlFor="knowledge-search">Search Knowledge</label>
            <input id="knowledge-search" name="q" placeholder="Search articles, questions, and published guides" />
            <button className="bhava-button bhava-button--primary" type="submit">Search</button>
          </form>

          <div className="knowledge-mega" aria-label="Knowledge pathways">
            {GROUPS.map((group) => (
              <div key={group.title} className="knowledge-mega-col">
                <h2>{group.title}</h2>
                <ul className="plain-list">
                  {group.links.map((link) => (
                    <li key={link.href}><Link href={link.href}>{link.label}</Link></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>Published guides</h2>
          <ul className="plain-list">
            {articles.map((a) => (
              <li key={a.slug}>
                <Link href={`/knowledge/${a.slug}`}>{a.title}</Link>
                <span className="hint"> — {a.summary}</span>
              </li>
            ))}
          </ul>

          <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>Canonical questions</h2>
          <ul className="plain-list">
            {questions.map((q) => (
              <li key={q.slug}>
                <Link href={`/knowledge/questions/${q.slug}`}>{q.title}</Link>
              </li>
            ))}
          </ul>

          <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>Pathway shells</h2>
          <div className="scope-grid">
            {pathways.map((p) => (
              <article key={p.slug} className="scope-card">
                <h3 style={{ marginTop: 0 }}>
                  <Link href={`/knowledge/pathways/${p.slug}`}>{p.title}</Link>
                </h3>
                <p className="hint" style={{ marginBottom: 0 }}>
                  <span className={`editorial-status ${p.status === "published" ? "active" : "planned"}`}>
                    {p.status}
                  </span>
                </p>
              </article>
            ))}
          </div>

          <aside className="knowledge-roadmap-note" style={{ marginTop: "2.5rem" }}>
            <h2 className="section-heading">How publishing works</h2>
            <p className="hint">
              The researched topic roadmap is governed privately. Only approved and published resources appear on public Knowledge pages.
              Private editorial counts and filters live in the local studio — not as a public “finished content” claim.
            </p>
          </aside>
        </div>
      </section>
    </>
  );
}
