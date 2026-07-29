import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export default function SourcePermissionsPage() {
  return (
    <>
      <PageIntro
        eyebrow="Sources & permissions"
        title="Shared with reverence and care."
        body="Every story clearly identifies its provenance so families and teachers can trust what they read."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <article className="feature-card">
            <h2>Provenance categories</h2>
            <p className="hint">
              Each story package carries a <code>permissions_status</code> field describing its content origin.
            </p>
            <dl style={{ marginTop: "0.75rem", lineHeight: 1.65 }}>
              <dt><strong>bhava_original</strong></dt>
              <dd style={{ marginLeft: "1.5rem", marginBottom: "0.5rem" }}>
                Original retelling written for Bhāva. Not a reproduction of any copyrighted text.
              </dd>
              <dt><strong>bbt_source_reference</strong></dt>
              <dd style={{ marginLeft: "1.5rem", marginBottom: "0.5rem" }}>
                Story references or draws from BBT publications (e.g. KRSNA Book).
                Bhāva does not republish full BBT texts. Śloka panels and quotations
                require documented permission before display.
              </dd>
              <dt><strong>third_party</strong></dt>
              <dd style={{ marginLeft: "1.5rem", marginBottom: "0.5rem" }}>
                Content sourced from a non-BBT third party. Documented permission is required;
                the phrase &ldquo;used with permission&rdquo; must never appear without verifiable documentation.
              </dd>
              <dt><strong>pending_review</strong></dt>
              <dd style={{ marginLeft: "1.5rem", marginBottom: "0.5rem" }}>
                Provenance has not yet been reviewed by the steward. Content may be restricted until cleared.
              </dd>
            </dl>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>What you will see</h2>
            <p className="hint">
              Source and scripture fields come from each locked package&apos;s manifest. Śloka panels stay empty until curated
              verses are supplied — we will not invent them.
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>Need a correction?</h2>
            <p className="hint">
              If a source or asset needs review, please reach the steward through the{" "}
              <Link href="/contact">contact page</Link>.
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
