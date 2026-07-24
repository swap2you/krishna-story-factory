import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Knowledge editorial (local)",
  robots: { index: false, follow: false },
};

export default function KnowledgeStudioPage() {
  return (
    <>
      <PageIntro
        eyebrow="Local studio"
        title="Knowledge editorial boundary"
        body="Private editorial workflows for Knowledge stay loopback-oriented. This page is a status shell — not a public CMS — and must not appear in public navigation."
      />
      <section className="section">
        <div className="container prose" style={{ maxWidth: 720 }}>
          <p>
            File-first content lives under <code>content/knowledge/</code>. Draft and restricted records never enter the public loader.
          </p>
          <p className="hint">
            Factory and Knowledge studio actions remain disabled by default. No AI auto-publish. No public comments.
          </p>
        </div>
      </section>
    </>
  );
}
