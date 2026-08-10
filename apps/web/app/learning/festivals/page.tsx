import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Festival use — Learning",
  description:
    "Planned festival learning pathway with honest links to Sunday School festival shells and the Krishna Book library.",
};

const FESTIVAL_SHELLS = [
  "Janmāṣṭamī",
  "Gaura Pūrṇimā",
  "Rāma Navamī",
  "Govardhana Pūjā",
  "Ratha-yātrā",
];

const LINKS = [
  {
    title: "Sunday School festival-unit cards",
    href: "/sunday-school",
    body: "Named festival unit shells live on the Sunday School page — each marked Planned until story-linked packs exist.",
    status: "available" as const,
  },
  {
    title: "Krishna Book stories",
    href: "/library/krishna-book",
    body: "Use released stories for seasonal listening while dedicated festival packs are prepared.",
    status: "available" as const,
  },
  {
    title: "Printables",
    href: "/printables",
    body: "Released story print assets suitable for festival craft tables — story by story, not as a fake festival ZIP.",
    status: "available" as const,
  },
];

export default function FestivalsLearningPage() {
  return (
    <>
      <PageIntro
        eyebrow="Learning · Festivals"
        title="Seasonal programs — named honestly."
        body="Multi-week festival packs are Planned. This page does not offer fake downloads; it points to real Sunday School shells and released stories."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="section-lead" style={{ marginTop: 0 }}>
            <span className="editorial-status planned">Planned pathway</span>
          </p>

          <h2 className="section-heading">Festival units (Planned)</h2>
          <p className="section-lead">
            These names match the Sunday School planner. Packs are not ready for download.
          </p>
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            {FESTIVAL_SHELLS.map((name) => (
              <article key={name} className="scope-card">
                <h3 style={{ marginTop: 0 }}>{name}</h3>
                <p style={{ marginBottom: ".85rem" }}>
                  Multi-week themed unit — stories, activities, and celebration notes still being prepared.
                </p>
                <span className="editorial-status planned">Planned</span>
              </article>
            ))}
          </div>

          <h2 className="section-heading">Use what exists now</h2>
          <div className="scope-grid">
            {LINKS.map((item) => (
              <article key={item.title} className="scope-card">
                <h3 style={{ marginTop: 0 }}>
                  <Link href={item.href}>{item.title}</Link>
                </h3>
                <p style={{ marginBottom: ".85rem" }}>{item.body}</p>
                <span className="editorial-status active">Available</span>
              </article>
            ))}
          </div>
          <p className="hint" style={{ marginTop: "2rem" }}>
            Back to the <Link href="/learning">Learning hub</Link>.
          </p>
        </div>
      </section>
    </>
  );
}
