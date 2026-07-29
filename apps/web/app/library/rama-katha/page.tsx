import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Rāma-kathā",
  description: "Supplementary Lord Rāma narrations drawn from Purāṇic and Vaiṣṇava sources.",
};

export default function RamaKathaPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Rāma-kathā"
        body="Supplementary narrations about Lord Rāma drawn from Purāṇic literature, the Bhāgavatam, and other Vaiṣṇava sources."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Gather Rāma-related pastimes that extend beyond the Rāmāyaṇa proper — from the Bhāgavatam, Viṣṇu Purāṇa, and other authoritative texts.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Families and students who have enjoyed Rāmāyaṇa stories and want to explore additional Rāma pastimes from diverse scriptural sources.</p>
            </article>
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>Individual narration packages with clear provenance — each story will cite its Purāṇic source, chapter, and verse range.</p>
            </article>
          </div>
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Rāma-kathā collection in planning</h2>
              <p>
                Stories will be curated from verified scriptural sources with full attribution.
                No content has been released yet — each narration requires editorial approval.
              </p>
              <p className="hint" style={{ marginTop: "1rem" }}>
                <span className="editorial-status planned">Planned</span>
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
