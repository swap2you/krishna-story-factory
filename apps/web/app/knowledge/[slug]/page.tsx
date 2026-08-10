import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArticleRecordShell } from "@/components/knowledge/article-record-shell";
import { getBySlug, listArticles } from "@/lib/knowledge/loader";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return listArticles().map((a) => ({ slug: a.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const doc = getBySlug(slug);
  if (!doc) return { title: "Not found" };
  return { title: doc.title, description: doc.summary };
}

export default async function KnowledgeArticlePage({ params }: Props) {
  const { slug } = await params;
  const doc = getBySlug(slug);
  if (!doc || !doc.body_md) notFound();

  return (
    <section className="section">
      <div className="container" style={{ maxWidth: 860 }}>
        <ArticleRecordShell doc={doc} />
      </div>
    </section>
  );
}
