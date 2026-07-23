import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";

export default function AboutPage() {
  return (
    <>
      <PageIntro
        eyebrow="About Bhāva"
        title="An independent home for gentle Krishna Book learning."
        body="Bhāva is an independent devotional-learning initiative stewarded by Svarna Gauranga Das in the Harrisburg, Pennsylvania area."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <article className="contact-card">
            <p className="eyebrow">Purpose</p>
            <h2>Who Bhāva serves</h2>
            <p>
              We begin with child-friendly Krishna Book learning for children, parents, teachers,
              Sunday Schools, and preachers — stories to listen to, read, color, and discuss without hurry.
            </p>
            <p className="hint" style={{ marginTop: "1rem" }}>
              AI may assist with drafting and tooling, while source fidelity and human devotional review remain required.
              Bhāva is not an official BBT publication and does not claim ownership of BBT source works.
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
