import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions } from "@/lib/knowledge/loader";
import { brandSrc } from "@/lib/brand-assets";

export const metadata: Metadata = {
  title: "Bhāva Knowledge Library",
  description: "Curated devotional documentation for families, teachers, and preachers — not an open forum.",
};

export default function KnowledgeHomePage() {
  const pathways = listPathways();
  const articles = listArticles();
  const questions = listQuestions();

  return (
    <>
      <PageIntro
        eyebrow="Knowledge"
        title="Bhāva Knowledge Library"
        body="A curated documentation library for Krishna Book learning, practice pathways, and carefully reviewed Q&A. Public submissions never publish automatically."
        heroSrc={brandSrc("collection-bhakti-blog")}
      />
      <section className="section">
        <div className="container">
          <form className="search-bar" action="/knowledge/search" method="get">
            <label className="sr-only" htmlFor="knowledge-search">Search Knowledge</label>
            <input id="knowledge-search" name="q" placeholder="Search articles and questions" />
            <button className="bhava-button bhava-button--primary" type="submit">Search</button>
          </form>

          <h2 className="section-heading" style={{ marginTop: "2rem" }}>Pathways</h2>
          <div className="scope-grid">
            {pathways.map((p) => (
              <article key={p.slug} className="scope-card">
                <h3 style={{ marginTop: 0 }}>{p.title}</h3>
                <p className="hint" style={{ marginBottom: 0 }}>
                  <span className={`editorial-status ${p.status === "published" ? "active" : "planned"}`}>
                    {p.status}
                  </span>
                </p>
              </article>
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

          <p className="hint" style={{ marginTop: "2rem" }}>
            Browse: <Link href="/knowledge/topics">Topics</Link>
            {" · "}
            <Link href="/knowledge/prayers">Prayers</Link>
            {" · "}
            <Link href="/knowledge/slokas">Ślokas</Link>
            {" · "}
            <Link href="/knowledge/ask">Ask privately</Link>
            {" · "}
            <Link href="/knowledge/corrections">Suggest a correction</Link>
          </p>
        </div>
      </section>
    </>
  );
}
