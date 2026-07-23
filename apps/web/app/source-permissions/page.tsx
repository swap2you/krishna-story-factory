import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export default function SourcePermissionsPage() {
  return (
    <>
      <PageIntro
        eyebrow="Sources & permissions"
        title="Shared with reverence and care."
        body="Story pages identify available package references. Content is for devotional learning and remains subject to editorial and rights review."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <article className="feature-card">
            <h2>What you will see</h2>
            <p className="hint">
              Source and scripture fields come from each locked package’s manifest. Śloka panels stay empty until curated
              verses are supplied — we will not invent them.
            </p>
          </article>
          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>Need a correction?</h2>
            <p className="hint">
              If a source or asset needs review, please reach the steward through the{" "}
              <Link href="/contact">contact page</Link> (Svarna Gauranga Das).
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
