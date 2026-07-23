import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Caitanya-caritāmṛta",
  description: "The life and teachings of Śrī Caitanya Mahāprabhu, adapted as stories for children and families.",
};

export default function CaitanyaCaritamrtaPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Caitanya-caritāmṛta"
        body="Kṛṣṇadāsa Kavirāja Gosvāmī's definitive biography of Śrī Caitanya Mahāprabhu — adapted as devotional stories for young listeners."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Retell the Ādi, Madhya, and Antya līlās of Lord Caitanya as age-appropriate stories, making the saṅkīrtana movement's history accessible to children.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Gauḍīya Vaiṣṇava families, ISKCON Sunday schools, and anyone interested in Lord Caitanya's pastimes and teachings.</p>
            </article>
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>Stories organized by līlā section (Ādi, Madhya, Antya), each citing original chapter and verse references from the Caitanya-caritāmṛta.</p>
            </article>
          </div>
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Caitanya-caritāmṛta stories in preparation</h2>
              <p>
                This collection demands particular care with philosophical content and biographical accuracy.
                No stories have been released — development follows the same source-governed editorial process.
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
