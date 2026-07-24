import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Scriptures" };

export default function Page() {
  const articles = listArticles();
  const questions = listQuestions();
  const pathways = listPathways();
  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Scriptures" body="Scripture indexes link to Library collections. Knowledge holds editorial guides, not full books." />
      <section className="section">
        <div className="container">
          <ul className="plain-list"><li><Link href="/library/krishna-book">Krishna Book</Link></li><li><Link href="/library/srimad-bhagavatam">Śrīmad-Bhāgavatam</Link></li><li><Link href="/library/bhagavad-gita">Bhagavad-gītā</Link></li></ul>
          <p className="hint" style={{ marginTop: "1.5rem" }}><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
