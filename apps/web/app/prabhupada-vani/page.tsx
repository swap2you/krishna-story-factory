import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Prabhupāda Vāṇī",
  description: "Curated categories of Śrīla Prabhupāda's instructions — lectures, walks, conversations, letters, and more — arriving with proper source attribution.",
};

const CATEGORIES = [
  {
    icon: "🎙",
    title: "Lectures",
    desc: "Recorded class lectures on Bhagavad-gītā, Śrīmad-Bhāgavatam, and Caitanya-caritāmṛta — curated excerpts with date, location, and verse reference.",
    audience: "All ages with parental context",
  },
  {
    icon: "🌅",
    title: "Morning Walks",
    desc: "Transcribed conversations from Śrīla Prabhupāda's morning walks — selected passages with historical context and participant notes.",
    audience: "Teenagers and adults",
  },
  {
    icon: "💬",
    title: "Conversations",
    desc: "Room conversations with guests, disciples, and scholars — selected for accessibility and relevance to family devotional life.",
    audience: "Older students and parents",
  },
  {
    icon: "✉️",
    title: "Letters",
    desc: "Personal letters of instruction and encouragement — selected with appropriate permissions and context for the reader.",
    audience: "Teachers and parents",
  },
  {
    icon: "🎤",
    title: "Interviews",
    desc: "Media interviews and public engagements — selected clips and transcripts showing Śrīla Prabhupāda's interactions with the wider world.",
    audience: "Teenagers and adults",
  },
  {
    icon: "🙏",
    title: "Pastimes & Remembrances",
    desc: "Stories and memories shared by disciples — curated respectfully with attribution to the narrator and occasion.",
    audience: "All ages",
  },
  {
    icon: "🧒",
    title: "For Children",
    desc: "Short, age-appropriate selections introducing children to Śrīla Prabhupāda's words — simple language, warm context, and parental guidance notes.",
    audience: "Ages 5–10",
  },
  {
    icon: "📖",
    title: "For Teenagers",
    desc: "Selections addressing identity, purpose, and spiritual practice — themes relevant to adolescent life, presented with discussion prompts.",
    audience: "Ages 11–17",
  },
];

export default function PrabhupadaVaniPage() {
  return (
    <>
      <PageIntro
        eyebrow="Prabhupāda Vāṇī"
        title="A space for timeless instruction."
        body="Prepared with care, context, and appropriate source attribution — never as a placeholder dump."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2.5rem" }}>
            <article className="scope-card">
              <h3>Source governance</h3>
              <p>Every item will cite its original source — lecture date and location, letter recipient and date, walk participants and city. No content is scraped, paraphrased, or fabricated.</p>
            </article>
            <article className="scope-card">
              <h3>Permissions</h3>
              <p>Content will be published only with appropriate permissions from the Bhaktivedanta Book Trust and other rights holders. Until permissions are confirmed, categories remain planned.</p>
            </article>
          </div>

          <h2 className="section-heading">Categories</h2>
          <p className="section-lead">Each category will open when curated selections and source permissions are ready.</p>
          <div className="category-grid">
            {CATEGORIES.map((cat) => (
              <article key={cat.title} className="category-card">
                <span style={{ fontSize: "1.6rem", display: "block", marginBottom: ".5rem" }} aria-hidden="true">{cat.icon}</span>
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
              <p className="eyebrow">Coming soon</p>
              <h2>Instruction with reverence</h2>
              <p>
                Prabhupāda Vāṇī will open when curated selections and permissions are ready.
                Until then, enjoy Krishna Book stories in the library.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
