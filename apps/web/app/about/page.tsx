import { PageIntro } from "@/components/page-intro";

export default function AboutPage() {
  return (
    <>
      <PageIntro
        eyebrow="About Bhāva"
        title="A gentle, premium home for devotional learning."
        body="Stories, listening, coloring, and quiet practice — designed so families can make a little space for Krishna in ordinary days."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="feature-grid">
            <article className="feature-card">
              <span className="icon" aria-hidden="true">❀</span>
              <h2>Radha-Krishna mood</h2>
              <p className="hint">Warm lotus, gold, and midnight tones for a calm, luxurious reading atmosphere.</p>
            </article>
            <article className="feature-card">
              <span className="icon" aria-hidden="true">ॐ</span>
              <h2>Faithful sources</h2>
              <p className="hint">Package references stay visible. We never invent ślokas or republish unlicensed books.</p>
            </article>
            <article className="feature-card">
              <span className="icon" aria-hidden="true">✦</span>
              <h2>Family & classroom</h2>
              <p className="hint">Listen, read Markdown stories, print PDFs, and keep private notes on this device only.</p>
            </article>
          </div>
          <article className="contact-card" style={{ marginTop: "1.25rem", maxWidth: 760 }}>
            <p className="eyebrow">Stewardship</p>
            <h2>Guided with care</h2>
            <p>
              Bhāva is stewarded by <strong>Svarna Gauranga Das</strong>. We value thoughtful review, accessible design,
              and an unhurried pace.
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
