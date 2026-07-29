import { PageIntro } from "@/components/page-intro";

export default function PrivacyPage() {
  return (
    <>
      <PageIntro
        eyebrow="Privacy"
        title="Your family’s notes stay on this device."
        body="Bhāva is designed for local, respectful use — especially around children’s learning."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <article className="feature-card">
            <h2>What stays local</h2>
            <p className="hint">
              Family notes, classroom playlists, and reading preferences are stored in your browser (localStorage). Bhāva
              does not upload child notes to a cloud account.
            </p>
          </article>
          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>What the catalog uses</h2>
            <p className="hint">
              The local API indexes package manifests already on your machine. Contact links may open the steward’s
              public website. Steward: <strong>Svarna Gauranga Das</strong>.
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
