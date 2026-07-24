import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Recently updated" };

export default function Page() {
  const articles = listArticles();
  const questions = listQuestions();
  const pathways = listPathways();
  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Recently updated" body="Published Knowledge resources, newest first by title until revision dates are tracked." />
      <section className="section">
        <div className="container">
          <ul className="plain-list">{articles.map((a) => (<li key={a.slug}><Link href={`/knowledge/${a.slug}`}>{a.title}</Link></li>))}</ul>
          <p className="hint" style={{ marginTop: "1.5rem" }}><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
