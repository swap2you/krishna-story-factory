import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Daśāvatāra",
  description: "The ten principal avatāras of Lord Viṣṇu, retold as devotional bedtime stories for children.",
};

const AVATARAS = [
  { name: "Matsya", desc: "The fish incarnation who saved the Vedas during the great deluge." },
  { name: "Kūrma", desc: "The tortoise who supported Mount Mandara during the churning of the ocean." },
  { name: "Varāha", desc: "The boar who rescued the Earth from the depths of the Garbhodaka ocean." },
  { name: "Nṛsiṁha", desc: "The half-man, half-lion who protected Prahlāda from Hiraṇyakaśipu." },
  { name: "Vāmana", desc: "The dwarf brāhmaṇa who reclaimed the three worlds from Bali Mahārāja." },
  { name: "Paraśurāma", desc: "The warrior sage who restored order among the kṣatriya class." },
  { name: "Rāmacandra", desc: "The ideal king of Ayodhyā who vanquished Rāvaṇa." },
  { name: "Kṛṣṇa", desc: "The Supreme Personality of Godhead who appeared in Vṛndāvana." },
  { name: "Buddha", desc: "The compassionate teacher who redirected misguided Vedic ritualism." },
  { name: "Kalki", desc: "The future avatāra who will appear at the end of Kali-yuga." },
];

export default function DasavataraPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Daśāvatāra"
        body="Ten principal avatāras of Lord Viṣṇu — from Matsya to Kalki — retold as devotional stories for children and families."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Present each avatāra's pastimes as a standalone story with scriptural references, connecting children to the broader Vaiṣṇava understanding of divine descent.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>Children ages 5–13 and families wanting an overview of Lord Viṣṇu's ten most celebrated incarnations.</p>
            </article>
          </div>

          <h2 className="section-heading">The Ten Avatāras</h2>
          <div className="scope-grid">
            {AVATARAS.map((a, i) => (
              <article key={a.name} className="scope-card">
                <h3><span style={{ color: "var(--bhava-saffron)", marginRight: ".5rem" }}>{i + 1}.</span>{a.name}</h3>
                <p>{a.desc}</p>
              </article>
            ))}
          </div>

          <div className="coming" style={{ marginTop: "2rem" }}>
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Daśāvatāra stories in planning</h2>
              <p>
                Each avatāra story will include Bhāgavatam and Purāṇic references, narration audio, coloring pages,
                and activity sheets. No content has been released yet.
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
