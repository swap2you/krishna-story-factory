import Link from "next/link";
import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";

export default function ContactPage() {
  return (
    <>
      <PageIntro
        eyebrow="Contact"
        title="Let's stay in touch."
        body="Bhāva is stewarded with care. Reach out for questions, feedback, or partnership ideas."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container contact-grid">
          <article className="contact-card">
            <p className="eyebrow">Steward</p>
            <h2>{contact.steward_name}</h2>
            <p className="hint">
              For families, teachers, and partners who want a calm home for Krishna Book learning.
            </p>
            <div className="actions" style={{ marginTop: "1.25rem" }}>
              <a className="bhava-button bhava-button--accent" href={`mailto:${contact.public_email}`}>
                Email {contact.steward_name}
              </a>
            </div>
          </article>
          <article className="contact-card">
            <p className="eyebrow">Links</p>
            <h2>Find Bhāva online</h2>
            <p><a href={`mailto:${contact.public_email}`}>{contact.public_email}</a></p>
            <p style={{ marginTop: "1rem" }}>
              <Link href="/privacy">Privacy</Link>
              {" · "}
              <Link href="/source-permissions">Sources</Link>
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
