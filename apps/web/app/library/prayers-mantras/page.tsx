import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Prayers & Mantras",
  description: "Morning prayers, key ślokas, and daily mantras for devotional families and classrooms.",
};

const PLANNED_SECTIONS = [
  { title: "Morning prayers", desc: "Prātaḥ-smaraṇam and daily prayers for children — with pronunciation guides and meaning." },
  { title: "Key ślokas", desc: "Essential Bhagavad-gītā and Bhāgavatam verses every young devotee benefits from learning." },
  { title: "Mahā-mantra", desc: "The Hare Kṛṣṇa mahā-mantra with context, melody guides, and age-appropriate explanations." },
  { title: "Guru prayers", desc: "Prayers to the spiritual master and the disciplic succession, with transliteration and meaning." },
  { title: "Festival prayers", desc: "Seasonal prayers for Janmāṣṭamī, Rāma Navamī, Gaura Pūrṇimā, and other holy days." },
  { title: "Bedtime prayers", desc: "Gentle evening prayers and ślokas suitable for the end of the day." },
];

export default function PrayersMantrasPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Prayers & Mantras"
        body="A curated home for morning prayers, key ślokas, the mahā-mantra, and devotional mantras — presented with pronunciation, meaning, and care."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Provide families and teachers with properly sourced, transliterated prayers and mantras — each with context, pronunciation audio, and age-appropriate explanations.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Children learning daily devotional practice, parents establishing a home sādhana routine, and Sunday school teachers structuring prayer time.</p>
            </article>
          </div>

          <h2 className="section-heading">Planned sections</h2>
          <div className="scope-grid">
            {PLANNED_SECTIONS.map((s) => (
              <article key={s.title} className="scope-card">
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </article>
            ))}
          </div>

          <div className="coming" style={{ marginTop: "2rem" }}>
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Prayers collection in preparation</h2>
              <p>
                Every prayer and śloka will include proper Sanskrit/Bengali transliteration, word-by-word meaning, and audio pronunciation.
                No content will be published without verification against authoritative sources.
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
