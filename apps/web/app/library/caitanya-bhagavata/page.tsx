import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Caitanya-bhāgavata",
  description: "Vṛndāvana Dāsa Ṭhākura's account of Śrī Caitanya Mahāprabhu, adapted for young readers.",
};

export default function CaitanyaBhagavataPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Caitanya-bhāgavata"
        body="Vṛndāvana Dāsa Ṭhākura's vivid, devotional account of Lord Caitanya's early pastimes — adapted with care for children and families."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Bring to life the Ādi, Madhya, and Antya khaṇḍas of the Caitanya-bhāgavata, focusing on Lord Caitanya's childhood, student life, and the start of the saṅkīrtana movement.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Young readers ages 6–13, families in the Gauḍīya tradition, and teachers wanting engaging Caitanya-era material for the classroom.</p>
            </article>
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>Narrations from each khaṇḍa with source chapter references, audio, coloring pages, and activity sheets — following the same editorial standards as all Bhāva collections.</p>
            </article>
          </div>
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Caitanya-bhāgavata stories in planning</h2>
              <p>
                Vṛndāvana Dāsa Ṭhākura's text is rich with devotional emotion and detail. Stories will be adapted
                faithfully with proper khaṇḍa and chapter citations. No content has been released yet.
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
