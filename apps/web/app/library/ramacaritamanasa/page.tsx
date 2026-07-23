import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Rāmacaritamānasa",
  description: "Tulasīdāsa's beloved retelling of Lord Rāma's pastimes, adapted for children and families.",
};

export default function RamacaritamanasaPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Rāmacaritamānasa"
        body="Gosvāmī Tulasīdāsa's beloved Hindi retelling of Lord Rāma's pastimes — presented for young listeners with cultural context and source care."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Adapt select episodes from the Rāmacaritamānasa's seven kāṇḍas as devotional stories, noting where Tulasīdāsa's narration differs from or enriches Vālmīki's account.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Hindi-speaking families, North Indian devotional communities, and anyone interested in Tulasīdāsa's poetic vision of Lord Rāma's līlā.</p>
            </article>
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>Selected episodes organized by kāṇḍa, each with cultural notes, original doha/chaupai references, and age-appropriate storytelling.</p>
            </article>
          </div>
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Mānasa stories in preparation</h2>
              <p>
                This collection requires careful handling of Tulasīdāsa's original verses and cultural context.
                No content has been released yet — preparation is underway.
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
