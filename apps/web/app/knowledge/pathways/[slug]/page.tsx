import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PageIntro } from "@/components/page-intro";
import { listPathways, searchKnowledge } from "@/lib/knowledge/loader";

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

  return (
    <>
      <PageIntro
        eyebrow="Knowledge pathway"
        title={pathway.title}
        body={
          pathway.status === "published"
            ? "Published pathway shell with reviewed Knowledge resources linked below."
            : "Pathway shell reserved for curated resources. Related roadmap topics remain editorial until approved."
        }
      />
      <section className="section">
        <div className="container prose" style={{ maxWidth: 820 }}>
          <p>
            Status:{" "}
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
            <p className="hint">No reviewed public resources are attached to this pathway yet.</p>
          )}
          <p><Link href="/knowledge">← Knowledge home</Link></p>
        </div>
      </section>
    </>
  );
}
