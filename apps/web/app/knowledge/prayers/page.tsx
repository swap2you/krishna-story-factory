import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Prayers & Āratis" };

export default function Page() {
  const articles = listArticles();
  const questions = listQuestions();
  const pathways = listPathways();
  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Prayers & Āratis" body="Reviewed prayer records will appear here. Full texts stay unpublished until permitted." />
      <section className="section">
        <div className="container">
          <p className="hint">No reviewed items published yet for this section.</p>
          <p className="hint" style={{ marginTop: "1.5rem" }}><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
