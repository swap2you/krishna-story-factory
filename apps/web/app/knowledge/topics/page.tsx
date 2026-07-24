import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listPathways } from "@/lib/knowledge/loader";

export const metadata: Metadata = { title: "Knowledge topics" };

export default function KnowledgeTopicsPage() {
  const pathways = listPathways();
  return (
    <>
      <PageIntro
        eyebrow="Knowledge"
        title="Topics and pathways"
        body="Governed topic shells for browsing. Only reviewed resources appear as published reading."
      />
      <section className="section">
        <div className="container">
          <ul className="plain-list">
            {pathways.map((p) => (
              <li key={p.slug}>
                <strong>{p.title}</strong>
                <span className="hint"> — {p.status}</span>
              </li>
            ))}
          </ul>
          <p className="hint"><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
