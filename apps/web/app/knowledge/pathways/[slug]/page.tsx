import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PageIntro } from "@/components/page-intro";
import { listArticles, listPathways, listQuestions, searchKnowledge } from "@/lib/knowledge/loader";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const pathway = listPathways().find((p) => p.slug === slug);
  return {
    title: pathway ? `${pathway.title} · Knowledge` : "Pathway",
    robots: pathway ? undefined : { index: false },
  };
}

export default async function KnowledgePathwayPage({ params }: Props) {
  const { slug } = await params;
  const pathway = listPathways().find((p) => p.slug === slug);
  if (!pathway) notFound();

  const related = searchKnowledge(pathway.title.split(" ")[0] || pathway.title);
  const articles = listArticles().slice(0, 3);
  const questions = listQuestions().slice(0, 3);

  return (
    <>
      <nav className="container" aria-label="Breadcrumb" style={{ paddingTop: "1.25rem" }}>
        <Link href="/knowledge">Knowledge</Link>
        <span aria-hidden="true"> / </span>
        <span>{pathway.title}</span>
      </nav>
      <PageIntro
        eyebrow="Knowledge pathway"
        title={pathway.title}
        body={
          pathway.status === "published"
            ? "This pathway gathers reviewed public resources for families, youth, and educators. More guides will appear here only after source and reviewer gates pass."
            : "This pathway shell is reserved for curated learning. Related roadmap topics remain private editorial work until approved — they are never auto-published from the 348-topic backlog."
        }
      />
      <section className="section">
        <div className="container knowledge-prose">
          <p>
            Audience: families, youth, and educators · Status:{" "}
            <span className={`editorial-status ${pathway.status === "published" ? "active" : "planned"}`}>
              {pathway.status}
            </span>
          </p>

          <h2>Published resources</h2>
          {related.length ? (
            <ul>
              {related.map((item) => (
                <li key={item.slug}>
                  <Link href={item.content_type === "canonical_question" ? `/knowledge/questions/${item.slug}` : `/knowledge/${item.slug}`}>
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <div className="audience-card">
              <p>
                No reviewed public resources are attached to this pathway yet. Use the published guides and questions
                below while this shelf is prepared.
              </p>
              <ul>
                {articles.map((a) => (
                  <li key={a.slug}><Link href={`/knowledge/${a.slug}`}>{a.title}</Link></li>
                ))}
              </ul>
            </div>
          )}

          <h2>Related questions</h2>
          <ul>
            {questions.map((q) => (
              <li key={q.slug}><Link href={`/knowledge/questions/${q.slug}`}>{q.title}</Link></li>
            ))}
          </ul>

          <h2>Related scriptures & printables</h2>
          <p>
            Explore the <Link href="/library">Library</Link> and <Link href="/printables">Printables</Link> for
            package-backed materials. Scripture shelves that are still planned stay clearly labeled.
          </p>

          <h2>What is coming next</h2>
          <p className="hint">
            Additional pathway articles publish only after rights, reviewer, and sacred-text gates clear. The private
            348-topic roadmap is editorial research data — not a public article count.
          </p>

          <p><Link href="/knowledge">← Return to Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
