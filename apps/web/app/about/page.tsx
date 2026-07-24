import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";

export default function AboutPage() {
  return (
    <>
      <PageIntro
        eyebrow="About Bhāva"
        title="Timeless devotion for growing hearts and minds."
        body="Bhāva is an independent devotional-learning platform stewarded by Svarna Gauranga Das in Harrisburg, Pennsylvania."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container knowledge-prose">
          <article className="contact-card">
            <h2>Mission</h2>
            <p>
              Bhāva serves children ages 5–20, families, Sunday School teachers, classroom teachers, and preachers with
              stories, scripture pathways, practice guidance, and printables — not only bedtime stories.
            </p>
            <h2>How content is produced</h2>
            <p>
              AI may assist drafting and factory tooling. Source fidelity, human devotional review, and publication
              gates remain required. Unreviewed sacred text is never published.
            </p>
            <h2>Stewardship</h2>
            <p>
              Bhāva is independent stewardship, not an official BBT publication, and does not claim ownership of BBT
              source works.
            </p>
            <p style={{ marginTop: "1rem" }}>
              Steward: <strong>{contact.steward_name}</strong> · {contact.location_city}, {contact.location_state}
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
