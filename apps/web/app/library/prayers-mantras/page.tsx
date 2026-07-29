import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Prayers & Mantras",
  description: "Planned prayer and mantra collections for devotional families and classrooms — with taxonomy, source requirements, and review status.",
};

interface PrayerCard {
  title: string;
  desc: string;
  audience: string;
  sourceReq: string;
  reviewReq: string;
}

const TAXONOMY: PrayerCard[] = [
  {
    title: "Śrīla Prabhupāda praṇati",
    desc: "Prayers to Śrīla Prabhupāda recited before class, with transliteration, word-by-word meaning, and pronunciation guide.",
    audience: "All ages — children, families, classrooms",
    sourceReq: "Verified Sanskrit/Bengali text from authorized prayer books",
    reviewReq: "Senior devotee review of transliteration and translation required",
  },
  {
    title: "Guru-praṇāma",
    desc: "Prayers to the spiritual master and the disciplic succession, presented with proper diacritics and context.",
    audience: "Students, families, Sunday Schools",
    sourceReq: "Authorized Gauḍīya Vaiṣṇava prayer sources",
    reviewReq: "Transliteration and meaning verified before publication",
  },
  {
    title: "Gurvaṣṭakam",
    desc: "Eight prayers glorifying the spiritual master by Śrīla Viśvanātha Cakravartī Ṭhākura — with verse-by-verse meaning.",
    audience: "Children and families learning morning prayers",
    sourceReq: "Original Sanskrit text with authorized translation",
    reviewReq: "Full text review — verse, transliteration, and word meaning",
  },
  {
    title: "Nṛsiṁha prayers & ārati",
    desc: "Prayers to Lord Nṛsiṁhadeva for protection, including the Nṛsiṁha ārati — with child-friendly context.",
    audience: "All ages — especially children learning evening prayers",
    sourceReq: "Authorized prayer text from Vaiṣṇava sources",
    reviewReq: "Devotional context and transliteration verified",
  },
  {
    title: "Tulasī ārati",
    desc: "Prayers and songs for Tulasī-devī worship, with transliteration and explanation of Tulasī's significance.",
    audience: "Families, children, Sunday Schools",
    sourceReq: "Traditional Tulasī prayers from Vaiṣṇava practice",
    reviewReq: "Transliteration and cultural context reviewed",
  },
  {
    title: "Prasādam prayers",
    desc: "Prayers offered before honoring prasādam — with pronunciation, meaning, and age-appropriate explanations.",
    audience: "Children, families, classroom meal time",
    sourceReq: "Standard Vaiṣṇava prasādam prayers",
    reviewReq: "Transliteration accuracy verified",
  },
  {
    title: "Daily prayers",
    desc: "Morning and evening prayers for devotional families — Prātaḥ-smaraṇam, maṅgala-ārati prayers, and bedtime recitations.",
    audience: "Families establishing daily devotional practice",
    sourceReq: "Authorized morning/evening prayer compilations",
    reviewReq: "Full transliteration and meaning review required",
  },
  {
    title: "Festival prayers",
    desc: "Seasonal prayers for Janmāṣṭamī, Rāma Navamī, Gaura Pūrṇimā, and other holy days — with context and celebration guides.",
    audience: "Families, Sunday Schools, festival organizers",
    sourceReq: "Festival-specific prayers from authorized sources",
    reviewReq: "Devotional context and occasion accuracy reviewed",
  },
];

export default function PrayersMantrasPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Prayers & Mantras"
        body="A curated home for daily prayers, guru prayers, ārati songs, and devotional mantras — each will include proper transliteration, word-by-word meaning, and audio pronunciation."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <nav aria-label="Breadcrumb" style={{ marginBottom: "1.5rem" }}>
            <span className="hint" style={{ fontSize: ".82rem" }}>
              <Link href="/" style={{ textDecoration: "none" }}>Home</Link>
              {" / "}
              <Link href="/library" style={{ textDecoration: "none" }}>Library</Link>
              {" / "}
              <span aria-current="page">Prayers &amp; Mantras</span>
            </span>
          </nav>

          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>
                Provide families and teachers with properly sourced, transliterated prayers
                and mantras — each with context, pronunciation audio, and age-appropriate explanations.
              </p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>
                Children learning daily devotional practice, parents establishing a home
                sādhana routine, and Sunday school teachers structuring prayer time.
              </p>
            </article>
          </div>

          <h2 className="section-heading">Planned prayer collections</h2>
          <div className="scope-grid">
            {TAXONOMY.map((card) => (
              <article key={card.title} className="scope-card">
                <h3>{card.title}</h3>
                <p>{card.desc}</p>
                <div style={{ marginTop: ".75rem", display: "flex", flexDirection: "column", gap: ".35rem" }}>
                  <span style={{ fontSize: ".82rem", color: "var(--bhava-muted)" }}>
                    <strong>Audience:</strong> {card.audience}
                  </span>
                  <span style={{ fontSize: ".82rem", color: "var(--bhava-muted)" }}>
                    <strong>Source:</strong> {card.sourceReq}
                  </span>
                  <span style={{ fontSize: ".82rem", color: "var(--bhava-muted)" }}>
                    <strong>Review:</strong> {card.reviewReq}
                  </span>
                  <span className="editorial-status planned" style={{ marginTop: ".35rem", width: "fit-content" }}>
                    Planned
                  </span>
                </div>
              </article>
            ))}
          </div>

          <div className="coming" style={{ marginTop: "2rem" }}>
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Prayers collection in preparation</h2>
              <p>
                Every prayer and śloka will include proper Sanskrit/Bengali transliteration,
                word-by-word meaning, and audio pronunciation. No content will be published
                without verification against authoritative sources and senior devotee review.
              </p>
              <p className="hint" style={{ marginTop: ".75rem" }}>
                Full texts and audio recordings will appear only after editorial review is complete.
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
