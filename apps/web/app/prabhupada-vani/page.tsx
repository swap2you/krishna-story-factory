import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { VaniCollectionCard } from "@/components/vani/vani-collection-card";
import { loadVaniCollection } from "@/lib/vani";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Prabhupāda Vāṇī",
  description:
    "A governed listening and study shelf for Śrīla Prabhupāda's source-verified instructions.",
};

const CATEGORIES = [
  {
    title: "Lectures",
    desc: "Class lectures on Bhagavad-gītā, Śrīmad-Bhāgavatam, and Caitanya-caritāmṛta — future curated excerpts will require date, location, and verse locator.",
    audience: "All ages with parental context",
  },
  {
    title: "Morning Walks",
    desc: "Morning-walk conversations — future selections will include historical context and participant notes from verified transcripts.",
    audience: "Teenagers and adults",
  },
  {
    title: "Conversations",
    desc: "Room conversations with guests, disciples, and scholars — selected only when rights and source context are confirmed.",
    audience: "Older students and parents",
  },
  {
    title: "Letters",
    desc: "Letters of instruction and encouragement — published only with appropriate permissions and full letter context.",
    audience: "Teachers and parents",
  },
  {
    title: "Interviews",
    desc: "Media interviews and public engagements — Planned shelf only until verified clips and transcripts clear review.",
    audience: "Teenagers and adults",
  },
  {
    title: "Pastimes & Remembrances",
    desc: "Disciple remembrances — curated with attribution to the narrator and occasion; never presented as Prabhupāda's own wording unless sourced.",
    audience: "All ages",
  },
  {
    title: "For Children",
    desc: "Age-appropriate introductions — Planned; no invented quotations for children.",
    audience: "Ages 5–10",
  },
  {
    title: "For Teenagers",
    desc: "Themes for adolescent life — Planned discussion prompts only after source-verified selections exist.",
    audience: "Ages 11–17",
  },
];

export default async function PrabhupadaVaniPage() {
  const archiveState = await loadVaniCollection();
  const collection =
    archiveState.status === "ok" && archiveState.data.tracks.length > 0
      ? archiveState.data
      : null;
  return (
    <>
      <PageIntro
        eyebrow="Prabhupāda Vāṇī"
        title="Hear the source. Keep the context."
        body="A calm, governed home for Śrīla Prabhupāda's recorded instructions. Available listening appears with provenance and honest restoration notes; planned shelves remain clearly marked."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          {collection ? (
            <VaniCollectionCard collection={collection} />
          ) : (
            <div className="coming vani-planned-state" role="status">
              <div>
                <p className="eyebrow">Krishna Book Dictation Archive</p>
                <h2>Collection preparation is in progress.</h2>
                <p>
                  The archive API has no verified public records right now. The collection will open here
                  only when source, audio, and rights review permit it—without invented substitutes.
                </p>
              </div>
            </div>
          )}

          <h2 className="section-heading vani-governance-heading">Trust & stewardship</h2>
          <div className="scope-grid" style={{ marginBottom: "2.5rem" }}>
            <article className="scope-card">
              <h3>What you can trust today</h3>
              <p>
                Available collections come from source-verified records. Planned shelves remain distinct,
                and no fabricated quotes, voice clones, or unauthorized transcript packs are published.
              </p>
            </article>
            <article className="scope-card">
              <h3>Planned — said honestly</h3>
              <p>
                Every category badge below means <strong>Planned</strong>, not available. The Krishna Book
                archive above is the primary collection only when its API returns reviewed records.
              </p>
            </article>
            <article className="scope-card">
              <h3>Source governance</h3>
              <p>
                Future items must cite original context — lecture date and location, letter recipient and date,
                walk participants and city. No scraped, paraphrased-as-quote, or fabricated wording.
              </p>
            </article>
            <article className="scope-card">
              <h3>Permissions</h3>
              <p>
                Content publishes only with appropriate permissions from the Bhaktivedanta Book Trust and other
                rights holders. Until then, categories remain Planned.
              </p>
            </article>
          </div>

          <div className="scope-grid" style={{ marginBottom: "2.5rem" }}>
            <article className="scope-card">
              <h3>What we will never do here</h3>
              <p>
                Fabricate quotations; present AI-generated first-person Prabhupāda dialogue; clone a voice;
                or strip teachings into decontextualized quote cards without source framing.
              </p>
            </article>
            <article className="scope-card">
              <h3>Suggest a correction</h3>
              <p>
                If you see an attribution error anywhere on Bhāva, use the private Knowledge routes:{" "}
                <Link href="/knowledge/corrections">Suggest a correction</Link>
                {" · "}
                <Link href="/knowledge/report-link">Report a broken link</Link>.
              </p>
            </article>
          </div>

          <h2 className="section-heading">Categories</h2>
          <p className="section-lead">
            Planned structure for future curated selections. These taxonomy cards are not playable records.
          </p>
          <div className="category-grid">
            {CATEGORIES.map((cat) => (
              <article key={cat.title} className="category-card" data-planned="true">
                <h3>{cat.title}</h3>
                <p>{cat.desc}</p>
                <div style={{ marginTop: ".75rem", display: "flex", flexWrap: "wrap", gap: ".5rem", alignItems: "center" }}>
                  <span className="editorial-status planned">Planned</span>
                  <span style={{ fontSize: ".8rem", color: "var(--bhava-muted)" }}>Audience: {cat.audience}</span>
                </div>
              </article>
            ))}
          </div>

          <div className="coming" style={{ marginTop: "2.5rem" }}>
            <div>
              <p className="eyebrow">Meanwhile</p>
              <h2>Study what is already reviewed</h2>
              <p>
                Alongside source recordings, continue with Krishna Book stories in the{" "}
                <Link href="/library/krishna-book">Library</Link> and source-led pages in{" "}
                <Link href="/knowledge">Knowledge</Link>.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
