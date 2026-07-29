import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PageIntro } from "@/components/page-intro";
import { getBySlug, listQuestions } from "@/lib/knowledge/loader";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return listQuestions().map((q) => ({ slug: q.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const doc = getBySlug(slug);
  if (!doc) return { title: "Not found" };
  return { title: doc.title, description: doc.summary };
}

export default async function KnowledgeQuestionPage({ params }: Props) {
  const { slug } = await params;
  const doc = getBySlug(slug);
  if (!doc || doc.content_type !== "question") notFound();

  return (
    <>
      <PageIntro eyebrow="Canonical Q&A" title={doc.title} body={doc.summary} />
      <section className="section">
        <div className="container prose" style={{ maxWidth: 760 }}>
          <p>{doc.answer_md}</p>
          <p className="hint">Review state: {doc.review_state}. Sources are editorial FAQ/privacy guidance.</p>
          <p className="hint">
            Was this helpful? Use <Link href="/knowledge/ask">Ask a follow-up</Link> or{" "}
            <Link href="/knowledge/corrections">Suggest a correction</Link> privately.
          </p>
          <p className="hint"><Link href="/knowledge/questions">← All questions</Link></p>
        </div>
      </section>
    </>
  );
}
