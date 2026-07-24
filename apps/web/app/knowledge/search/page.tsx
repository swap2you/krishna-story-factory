import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { searchKnowledge } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Search Knowledge" };
export const dynamic = "force-dynamic";

export default async function KnowledgeSearchPage({
  searchParams,
}: {
  searchParams?: Promise<{ q?: string }>;
}) {
  const params = searchParams ? await searchParams : {};
  const q = params.q ?? "";
  const results = searchKnowledge(q);

  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Search" body="Search published articles and canonical questions only." />
      <section className="section">
        <div className="container">
          <form className="search-bar" action="/knowledge/search" method="get">
            <label className="sr-only" htmlFor="q">Query</label>
            <input id="q" name="q" defaultValue={q} placeholder="Try Bhāva, printing, sources…" />
            <button className="bhava-button bhava-button--primary" type="submit">Search</button>
          </form>
          <ul className="plain-list" style={{ marginTop: "1.5rem" }}>
            {results.map((r) => (
              <li key={r.slug}>
                <Link href={r.content_type === "question" ? `/knowledge/questions/${r.slug}` : `/knowledge/${r.slug}`}>
                  {r.title}
                </Link>
                <span className="hint"> — {r.summary}</span>
              </li>
            ))}
          </ul>
          {!results.length ? (
            <p className="hint">
              No matches. Try another phrase or <Link href="/knowledge/ask">ask privately</Link>.
            </p>
          ) : null}
        </div>
      </section>
    </>
  );
}
