import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PageIntro } from "@/components/page-intro";
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
    <>
      <PageIntro eyebrow="Knowledge article" title={doc.title} body={doc.summary} />
      <section className="section">
        <div className="container prose" style={{ maxWidth: 760 }}>
          <p className="hint">
            Type: {doc.content_type}
            {doc.pathway ? ` · Pathway: ${doc.pathway}` : ""}
            {" · "}
            Review: {doc.review_state}
          </p>
          <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0 }}>{doc.body_md}</pre>
          <p className="hint" style={{ marginTop: "2rem" }}>
            <Link href="/knowledge">← Knowledge home</Link>
            {" · "}
            <Link href="/knowledge/corrections">Suggest a correction</Link>
          </p>
        </div>
      </section>
    </>
  );
}
