import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Śrīmad-Bhāgavatam",
  description: "Cantos 1–12 of the Śrīmad-Bhāgavatam, adapted as devotional bedtime stories for children and families.",
};

const CANTOS = [
  { num: 1, title: "Creation", summary: "The creation of the universe and the questions of the sages at Naimiṣāraṇya." },
  { num: 2, title: "The Cosmic Manifestation", summary: "The universal form, the process of creation, and the Lord's pastimes." },
  { num: 3, title: "The Status Quo", summary: "Kapila's teachings, Devahūti's inquiries, and the Varāha avatāra." },
  { num: 4, title: "The Creation of the Fourth Order", summary: "Dakṣa, Dhruva Mahārāja, and King Pṛthu." },
  { num: 5, title: "The Creative Impetus", summary: "The dynasty of Priyavrata and the structure of the universe." },
  { num: 6, title: "Prescribed Duties for Mankind", summary: "Ajāmila, Vṛtrāsura, and the Dakṣa-Śiva conflict." },
  { num: 7, title: "The Science of God", summary: "Prahlāda Mahārāja and Lord Nṛsiṁhadeva." },
  { num: 8, title: "Withdrawal of the Cosmic Creations", summary: "Gajendra, the Manvantara avatāras, and the churning of the ocean." },
  { num: 9, title: "Liberation", summary: "The dynasty of the Sun-god and the story of the Mahārājas." },
  { num: 10, title: "The Summum Bonum", summary: "The complete pastimes of Lord Śrī Kṛṣṇa in Vṛndāvana and beyond." },
  { num: 11, title: "General History", summary: "The Uddhava-gītā and the Lord's final instructions." },
  { num: 12, title: "The Age of Deterioration", summary: "Predictions for Kali-yuga and the conclusion of Bhāgavatam." },
];

export default function SrimadBhagavatamPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Śrīmad-Bhāgavatam"
        body="Twelve cantos of transcendental narration — the ripened fruit of Vedic literature. Stories will be adapted for young listeners with faithful source references."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Retell the Bhāgavatam's major narratives as age-appropriate bedtime stories, each linked to its original canto, chapter, and verse range.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Children ages 5–13, parents reading aloud, and Sunday school teachers seeking structured source material.</p>
            </article>
            <article className="scope-card">
              <h3>Editorial status</h3>
              <p><span className="editorial-status planned">Planned</span> — No stories released yet. Content will be curated with senior devotee review before publication.</p>
            </article>
          </div>

          <h2 className="section-heading">Browse by Canto</h2>
          <ul className="canto-list">
            {CANTOS.map((canto) => (
              <li key={canto.num}>
                <Link href={`/library/srimad-bhagavatam/canto/${canto.num}`}>
                  <span className="canto-num">{canto.num}</span>
                  <span>
                    <strong>{canto.title}</strong>
                    <span className="hint" style={{ display: "block", fontSize: ".85rem" }}>{canto.summary}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}
