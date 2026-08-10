import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  audienceLabel,
  getDerivativeBySlug,
  listPublicDerivativeMetas,
} from "@/lib/learning/derivatives";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return listPublicDerivativeMetas().map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const doc = getDerivativeBySlug(slug);
  if (!doc) return { title: "Not found" };
  return { title: doc.title, description: doc.learning_objective };
}

export default async function LearningDerivativePage({ params }: Props) {
  const { slug } = await params;
  const doc = getDerivativeBySlug(slug);
  if (!doc || !doc.body_md) notFound();

  return (
    <section className="section">
      <div className="container" style={{ maxWidth: 860 }}>
        <article className="knowledge-learning knowledge-learning--board-b knowledge-article-shell">
          <header className="knowledge-learning__hero">
            <p className="eyebrow">Learning derivative</p>
            <h1 className="knowledge-learning__title">{doc.title}</h1>
            <p className="knowledge-status knowledge-status--guide">
              Available · {doc.review_state} · Bhāva-original
            </p>
            <p className="knowledge-learning__purpose">{doc.learning_objective}</p>
          </header>

          <dl className="knowledge-source" style={{ marginBottom: "1.5rem" }}>
            <div>
              <dt>Audience</dt>
              <dd>{audienceLabel(doc)}</dd>
            </div>
            <div>
              <dt>Lineage</dt>
              <dd>
                Canonical Knowledge:{" "}
                <Link href={knowledgeHref(doc.canonical_record_version.record_slug)}>
                  {doc.canonical_record_version.record_slug}
                </Link>{" "}
                ({doc.canonical_record_version.record_version})
              </dd>
            </div>
            <div>
              <dt>Type</dt>
              <dd>{doc.derivative_type.replace(/_/g, " ")}</dd>
            </div>
            <div>
              <dt>Downloads</dt>
              <dd>
                {doc.export_manifest.downloadable
                  ? "Validated export available"
                  : "None — read in-page markdown only (no fake PDF)"}
              </dd>
            </div>
          </dl>

          <section
            className="prose"
            aria-label="Derivative body"
            style={{ maxWidth: 760 }}
          >
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0 }}>
              {doc.body_md}
            </pre>
          </section>

          <p className="hint" style={{ marginTop: "2rem" }}>
            <Link href="/learning">← Learning hub</Link>
            {" · "}
            <Link href="/knowledge">Knowledge pilot</Link>
            {" · "}
            <Link href="/knowledge/corrections">Suggest a correction</Link>
          </p>
        </article>
      </div>
    </section>
  );
}

function knowledgeHref(slug: string): string {
  if (
    slug === "is-bhava-official-bbt" ||
    slug === "does-bhava-collect-child-data" ||
    slug === "what-is-bhava-faq"
  ) {
    return `/knowledge/questions/${slug}`;
  }
  return `/knowledge/${slug}`;
}
