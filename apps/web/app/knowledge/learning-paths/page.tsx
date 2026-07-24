import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Learning paths" };

export default function Page() {
  const articles = listArticles();
  const questions = listQuestions();
  const pathways = listPathways();
  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Learning paths" body="Structured pathways for newcomers, families, and teachers. Seeded as governed shells." />
      <section className="section">
        <div className="container">
          <ul className="plain-list">{pathways.map((p) => (<li key={p.slug}><strong>{p.title}</strong> <span className="hint">— {p.status}</span></li>))}</ul>
          <p className="hint" style={{ marginTop: "1.5rem" }}><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
