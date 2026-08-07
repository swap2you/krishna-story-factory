import type { Metadata } from "next";
import { cookies, headers } from "next/headers";
import { notFound } from "next/navigation";
import { LearningPageShell } from "@/components/knowledge/learning-page-shell";
import { getKnowledgePackage, validateKnowledgePackage } from "@/lib/knowledge/packages";
import { isStudioAuthed, isLoopbackRequest } from "@/lib/knowledge/studio-guard";

export const metadata: Metadata = {
  title: "Knowledge private preview · TEST FIXTURE",
  robots: { index: false, follow: false, nocache: true },
};

export default async function KnowledgePreviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ lens?: string; focus?: string; stanza?: string }>;
}) {
  const { slug } = await params;
  const sp = await searchParams;
  const jar = await cookies();
  const hdrs = await headers();

  if (!isStudioAuthed(jar) || !isLoopbackRequest(hdrs)) {
    notFound();
  }

  const pkg = getKnowledgePackage(slug);
  if (!pkg) notFound();
  // Foundation preview is for private packages only.
  if (pkg.record.visibility === "public") notFound();

  const validation = validateKnowledgePackage(pkg);
  if (!validation.ok) {
    return (
      <section className="section">
        <div className="container">
          <p className="eyebrow">Studio</p>
          <h1>Package validation failed</h1>
          <p>{validation.errors.join("; ")}</p>
        </div>
      </section>
    );
  }

  return (
    <>
      <p className="sr-only">
        Loopback studio preview. Authenticated loopback-only private preview. Not indexed.
        Production scripture remains blocked.
      </p>
      <section className="section knowledge-preview-chrome">
        <div className="container" style={{ maxWidth: 900 }}>
          <p className="eyebrow">Loopback studio preview</p>
          <p className="hint">
            Authenticated loopback-only private preview. Not indexed. Production scripture remains
            blocked.
          </p>
          <LearningPageShell
            pkg={pkg}
            initialLens={sp.lens}
            initialFocus={sp.focus === "1"}
            initialStanza={sp.stanza}
          />
        </div>
      </section>
    </>
  );
}
