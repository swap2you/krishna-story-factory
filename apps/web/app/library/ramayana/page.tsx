import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Rāmāyaṇa",
  description: "The epic journey of Lord Rāma, adapted as devotional bedtime stories for children and families.",
};

export default function RamayanaPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Rāmāyaṇa"
        body="Vālmīki's timeless epic — the journey of Lord Rāma from Ayodhyā to Laṅkā and back, retold with devotion for young listeners."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Retell the major kāṇḍas (books) of the Rāmāyaṇa as bedtime stories, preserving the devotional mood while making the narrative accessible to children.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Families with children ages 5–13, home-schooling parents, and Sunday school teachers looking for structured Rāmāyaṇa material.</p>
            </article>
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>Stories organized by kāṇḍa — Bāla, Ayodhyā, Araṇya, Kiṣkindhā, Sundara, Yuddha, and Uttara — with audio, coloring, and source references.</p>
            </article>
          </div>
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Rāmāyaṇa stories are being prepared</h2>
              <p>
                Each story will reference its source kāṇḍa and sarga. Content enters production only after
                editorial review. No stories have been released for this collection yet.
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
