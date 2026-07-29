import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Questions & Answers" };

export default function Page() {
  const articles = listArticles();
  const questions = listQuestions();
  const pathways = listPathways();
  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Questions & Answers" body="Canonical FAQ answers curated for Bhāva. Public visitors cannot post answers." />
      <section className="section">
        <div className="container">
          <ul className="plain-list">{questions.map((q) => (<li key={q.slug}><Link href={`/knowledge/questions/${q.slug}`}>{q.title}</Link></li>))}</ul>
          <p className="hint" style={{ marginTop: "1.5rem" }}><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
