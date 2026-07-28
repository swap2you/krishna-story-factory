import { PageIntro } from "@/components/page-intro";
import contact from "@/config/contact.json";

export const metadata = {
  title: "Copyright & Permissions · Bhāva",
  description:
    "Copyright, publisher imprint, rights limitations, and permissions contact for Bhāva publications.",
};

export default function RightsPage() {
  const year = contact.website_copyright_year;
  return (
    <>
      <PageIntro
        eyebrow="Copyright & Permissions"
        title="Honest notices for original work — without overclaiming scripture."
        body="Bhāva publishes original adaptations, educational activities, design, and production under a clear rights framework. Preexisting scripture and third-party works remain with their rights holders."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <article className="feature-card">
            <h2>Public identity</h2>
            <p className="hint">
              Copyright owner / public attribution: <strong>{contact.copyright_owner}</strong>
              <br />
              Publisher / imprint: <strong>{contact.publisher}</strong> ({contact.publisher_role})
              <br />
              Project: <strong>{contact.project_name}</strong>
              <br />
              Location: {contact.location_city}, {contact.location_state}, {contact.location_country}
              <br />
              Contact:{" "}
              <a href={`mailto:${contact.public_email}`}>{contact.public_email}</a>
            </p>
            <p className="hint">
              Dauji Publication is named as a publishing imprint. It is not represented here as a
              registered corporation, trademark, or separate copyright owner.
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>Website notice</h2>
            <p className="hint">
              © {year} {contact.copyright_owner}. All rights reserved.
              <br />
              Published by {contact.publisher} · A {contact.project_name} Project publication
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>What the claim covers</h2>
            <p className="hint">
              Applicable original writing, child-friendly adaptation, selection and arrangement,
              educational activities, human-authored design or modification, editing, narration
              performed by a human, protectable human sound-production elements, website authorship,
              compilation, and production.
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>What is not claimed</h2>
            <p className="hint">
              Bhagavad-gītā, Śrīmad-Bhāgavatam, Krishna Book, Caitanya-caritāmṛta, Śrīla Prabhupāda’s
              books, purports, letters, lectures, and recordings; scriptural verses; traditional
              prayers and songs; third-party translations, artwork, photos, fonts, music, or
              recordings; Ministry resources; reference documents; public-domain facts; and purely
              AI-generated expressive material without sufficient human authorship.
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>AI assistance</h2>
            <p className="hint">
              Where AI tools assist drafting, imagery, or narration, package manifests record the
              human-authored contribution, provider provenance, and limitations. Prompting alone is
              not presented as authorship. Sound-recording ℗ claims are applied only when a reviewed
              sound-recording rights status supports them.
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>Registration</h2>
            <p className="hint">
              A copyright notice and evidence record are not the same as formal U.S. Copyright Office
              registration. Bhāva does not claim “registered” status unless an official record
              supports that claim.
            </p>
          </article>

          <article className="feature-card" style={{ marginTop: "1rem" }}>
            <h2>Corrections and permissions</h2>
            <p className="hint">
              For rights questions, corrections, or permission requests, email{" "}
              <a href={`mailto:${contact.public_email}`}>{contact.public_email}</a>. Linked or
              embedded third-party content remains with its respective owners.
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
