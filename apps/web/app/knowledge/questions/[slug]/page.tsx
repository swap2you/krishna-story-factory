import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { QuestionRecordShell } from "@/components/knowledge/question-record-shell";
import { getBySlug, getProvenance, listQuestions } from "@/lib/knowledge/loader";

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
  const provenance = getProvenance(slug);

  return (
    <section className="section">
      <div className="container" style={{ maxWidth: 860 }}>
        <QuestionRecordShell doc={doc} provenance={provenance} />
      </div>
    </section>
  );
}
