import { PageIntro } from "@/components/page-intro";

export default function AccessibilityPage() {
  return (
    <>
      <PageIntro
        eyebrow="Accessibility"
        title="Designed for welcoming use."
        body="Clear focus, keyboard paths, readable type, and calm motion — so more families can learn together."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container feature-grid">
          <article className="feature-card">
            <span className="icon" aria-hidden="true">◎</span>
            <h2>Focus & touch</h2>
            <p className="hint">Visible focus rings, keyboard-operable controls, and 44px+ touch targets.</p>
          </article>
          <article className="feature-card">
            <span className="icon" aria-hidden="true">Aa</span>
            <h2>Reading modes</h2>
            <p className="hint">Larger text, sepia, dark, and dyslexia-friendly spacing on story pages.</p>
          </article>
          <article className="feature-card">
            <span className="icon" aria-hidden="true">◐</span>
            <h2>Motion care</h2>
            <p className="hint">Decorative motion softens when your device requests reduced motion.</p>
          </article>
        </div>
      </section>
    </>
  );
}
