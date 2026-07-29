import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Bhagavad-gītā",
  description: "Verse-by-verse devotional stories from the Bhagavad-gītā, adapted for children and families.",
};

export default function BhagavadGitaPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Bhagavad-gītā"
        body="The Song of God — eighteen chapters of wisdom from the battlefield of Kurukṣetra, retold for young hearts."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Present the Gītā's teachings through age-appropriate narratives, connecting each chapter's theme to stories children can understand and remember.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Children ages 7–13 and families seeking an accessible entry into the Bhagavad-gītā's philosophy through storytelling.</p>
            </article>
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>Chapter-by-chapter story adaptations with verse references, key śloka cards, audio narration, and discussion prompts for parents and teachers.</p>
            </article>
          </div>
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Gītā stories in preparation</h2>
              <p>
                Content will be developed with careful verse attribution and senior devotee review.
                No chapters have been released yet — we will not publish until quality and accuracy are confirmed.
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
