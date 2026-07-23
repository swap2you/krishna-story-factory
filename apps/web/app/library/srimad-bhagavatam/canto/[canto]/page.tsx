import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { notFound } from "next/navigation";

const CANTO_INFO: Record<number, { title: string; summary: string }> = {
  1: { title: "Creation", summary: "The questions of the sages at Naimiṣāraṇya and the foundation of Śrīmad-Bhāgavatam." },
  2: { title: "The Cosmic Manifestation", summary: "The universal form and the process of cosmic creation." },
  3: { title: "The Status Quo", summary: "Kapila's teachings to Devahūti and the appearance of Varāha." },
  4: { title: "The Creation of the Fourth Order", summary: "The stories of Dakṣa, Dhruva, and King Pṛthu." },
  5: { title: "The Creative Impetus", summary: "The dynasty of Priyavrata and the structure of the universe." },
  6: { title: "Prescribed Duties for Mankind", summary: "Ajāmila's deliverance, Vṛtrāsura, and the story of Citraketu." },
  7: { title: "The Science of God", summary: "Prahlāda Mahārāja and the appearance of Lord Nṛsiṁhadeva." },
  8: { title: "Withdrawal of the Cosmic Creations", summary: "Gajendra's prayers, the Manvantara avatāras, and the churning of the milk ocean." },
  9: { title: "Liberation", summary: "The solar dynasty, the Ikṣvāku kings, and the pastimes of Lord Rāmacandra." },
  10: { title: "The Summum Bonum", summary: "The complete pastimes of Lord Śrī Kṛṣṇa — from birth in Mathurā to Dvārakā." },
  11: { title: "General History", summary: "The Uddhava-gītā and the Lord's final instructions before departure." },
  12: { title: "The Age of Deterioration", summary: "Predictions for Kali-yuga, the Bhāgavatam's conclusion, and the glories of hearing." },
};

type Props = { params: Promise<{ canto: string }> };

export async function generateStaticParams() {
  return Array.from({ length: 12 }, (_, i) => ({ canto: String(i + 1) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { canto } = await params;
  const num = Number(canto);
  const info = CANTO_INFO[num];
  if (!info) return { title: "Canto not found" };
  return {
    title: `Canto ${num} — ${info.title}`,
    description: info.summary,
  };
}

export default async function CantoPage({ params }: Props) {
  const { canto } = await params;
  const num = Number(canto);
  const info = CANTO_INFO[num];
  if (!info) notFound();

  const prev = num > 1 ? num - 1 : null;
  const next = num < 12 ? num + 1 : null;

  return (
    <>
      <PageIntro
        eyebrow={`Śrīmad-Bhāgavatam · Canto ${num}`}
        title={info.title}
        body={info.summary}
      />
      <section className="section">
        <div className="container" style={{ maxWidth: 760 }}>
          <div className="scope-grid">
            <article className="scope-card">
              <h3>Planned content</h3>
              <p>
                Age-appropriate bedtime stories drawn from Canto {num}, each with chapter and verse citations,
                audio narration, coloring pages, and activity sheets. No content has been released for this canto yet.
              </p>
            </article>
            <article className="scope-card">
              <h3>Editorial status</h3>
              <p>
                <span className="editorial-status planned">Planned</span> — Stories for this canto will be developed
                following the same faithful, source-governed process used for Krishna Book bedtime stories.
              </p>
            </article>
          </div>

          <div className="coming" style={{ marginTop: "2rem" }}>
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Stories from Canto {num} are being prepared</h2>
              <p>
                When ready, each story will include narration, illustrations, and verifiable references back to
                Śrīmad-Bhāgavatam Canto {num}. Until then, enjoy the released Krishna Book stories in the library.
              </p>
            </div>
          </div>

          <nav style={{ display: "flex", justifyContent: "space-between", marginTop: "2.5rem", gap: "1rem" }}>
            {prev ? (
              <Link href={`/library/srimad-bhagavatam/canto/${prev}`} className="bhava-button bhava-button--primary" style={{ textDecoration: "none" }}>
                ← Canto {prev}
              </Link>
            ) : <span />}
            <Link href="/library/srimad-bhagavatam" style={{ textDecoration: "none", fontWeight: 700 }}>
              All cantos
            </Link>
            {next ? (
              <Link href={`/library/srimad-bhagavatam/canto/${next}`} className="bhava-button bhava-button--primary" style={{ textDecoration: "none" }}>
                Canto {next} →
              </Link>
            ) : <span />}
          </nav>
        </div>
      </section>
    </>
  );
}
