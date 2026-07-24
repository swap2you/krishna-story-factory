import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listQuestions } from "@/lib/knowledge/loader";

export const metadata: Metadata = {
  title: "Knowledge index",
  description: "Alphabetical index of published Bhāva Knowledge resources.",
};

export default function KnowledgeIndexPage() {
  const items = [...listArticles(), ...listQuestions()].sort((a, b) =>
    a.title.localeCompare(b.title),
  );
  return (
    <>
      <PageIntro eyebrow="Knowledge" title="Alphabetical index" body="Published Knowledge resources only." />
      <section className="section">
        <div className="container">
          <ul className="plain-list">
            {items.map((item) => (
              <li key={item.slug}>
                <Link
                  href={
                    item.content_type === "canonical_question" || item.content_type === "question"
                      ? `/knowledge/questions/${item.slug}`
                      : `/knowledge/${item.slug}`
                  }
                >
                  {item.title}
                </Link>
                <span className="hint"> · {item.content_type}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}
