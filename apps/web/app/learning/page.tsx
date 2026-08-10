import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { brandSrc } from "@/lib/brand-assets";
import {
  audienceLabel,
  listPublicDerivatives,
} from "@/lib/learning/derivatives";

export const metadata: Metadata = {
  title: "Learning",
  description:
    "Honest learning pathways and Bhāva-original derivatives for children, families, Sunday School, teachers, and communities — linking only to real pages.",
};

type Pathway = {
  title: string;
  href: string;
  status: "available" | "planned";
  audience: string;
  body: string;
};

const PATHWAYS: Pathway[] = [
  {
    title: "Children & Youth",
    href: "/learning/children-youth",
    status: "available",
    audience: "Ages 5–20",
    body: "Age-band routes into stories, Knowledge, and printables — without treating teenagers like little children.",
  },
  {
    title: "Families",
    href: "/learning/families",
    status: "available",
    audience: "Homes and caregivers",
    body: "Calm home practice routes into Printables, public Knowledge guides, and published family derivatives.",
  },
  {
    title: "Sunday School",
    href: "/sunday-school",
    status: "available",
    audience: "Weekly classes",
    body: "Usable weekly planner plus a published teacher guide grounded in printing and permissions Knowledge.",
  },
  {
    title: "Teachers",
    href: "/teachers",
    status: "available",
    audience: "Classroom facilitators",
    body: "Classroom playlist helper and lesson packing tools grounded in released Krishna Book stories.",
  },
  {
    title: "Preachers",
    href: "/preachers",
    status: "available",
    audience: "Outreach and programs",
    body: "Select released stories, preview source references, and export outlines for programs.",
  },
  {
    title: "Gurukula / Homeschool",
    href: "/learning/gurukula-homeschool",
    status: "planned",
    audience: "Home and Gurukula educators",
    body: "Dedicated curriculum packs are still forming. This pathway links only to real Teachers, Knowledge, and Printables pages today.",
  },
  {
    title: "Festival use",
    href: "/learning/festivals",
    status: "planned",
    audience: "Seasonal programs",
    body: "Festival unit shells are named honestly. Multi-week packs are Planned; use Sunday School and Stories for what exists now.",
  },
];

export default function LearningHubPage() {
  const derivatives = listPublicDerivatives();

  return (
    <>
      <PageIntro
        eyebrow="Learning"
        title="Pathways for growing devotees."
        body="Learning serves children, families, teachers, preachers, and communities. Each pathway links only to a real page, with Available or Planned labeled honestly."
        heroSrc={brandSrc("collection-sunday-school")}
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Available now</h3>
              <p>
                Audience pathways below, plus {derivatives.length} published
                Bhāva-original derivative{derivatives.length === 1 ? "" : "s"}{" "}
                grounded in the public Knowledge pilot. In-page markdown only —
                no fake PDF downloads.
              </p>
            </article>
            <article className="scope-card">
              <h3>Still planned</h3>
              <p>
                Dedicated Gurukula/homeschool curriculum packs and festival unit
                packs remain Planned. They are labeled clearly so nothing looks
                published before it is ready.
              </p>
            </article>
          </div>

          <h2 className="section-heading">Published learning derivatives</h2>
          <p className="section-lead">
            Each item shows lineage, audience, objective, and review state.
            Downloads stay off until a validated export exists.
          </p>
          {derivatives.length ? (
            <div className="scope-grid" style={{ marginBottom: "2.5rem" }}>
              {derivatives.map((d) => (
                <article key={d.slug} className="scope-card">
                  <h3 style={{ marginTop: 0 }}>
                    <Link href={`/learning/derivatives/${d.slug}`}>{d.title}</Link>
                  </h3>
                  <p className="hint" style={{ marginBottom: ".5rem" }}>
                    {audienceLabel(d)}
                  </p>
                  <p style={{ marginBottom: ".65rem" }}>{d.learning_objective}</p>
                  <p className="hint" style={{ marginBottom: ".65rem" }}>
                    Lineage: {d.canonical_record_version.record_slug} · Review:{" "}
                    {d.review_state} ·{" "}
                    {d.export_manifest.downloadable
                      ? "Export validated"
                      : "In-page only (no download)"}
                  </p>
                  <span className="editorial-status active">Available</span>
                </article>
              ))}
            </div>
          ) : (
            <p className="hint" style={{ marginBottom: "2.5rem" }}>
              No public derivatives are published yet.
            </p>
          )}

          <h2 className="section-heading">Learning pathways</h2>
          <p className="section-lead">
            Choose a pathway. Planned destinations stay open as honest shells —
            never as fake downloads.
          </p>
          <div className="scope-grid">
            {PATHWAYS.map((pathway) => (
              <article key={pathway.href} className="scope-card">
                <h3 style={{ marginTop: 0 }}>
                  <Link href={pathway.href}>{pathway.title}</Link>
                </h3>
                <p className="hint" style={{ marginBottom: ".65rem" }}>
                  {pathway.audience}
                </p>
                <p style={{ marginBottom: ".85rem" }}>{pathway.body}</p>
                <span
                  className={`editorial-status ${pathway.status === "available" ? "active" : "planned"}`}
                >
                  {pathway.status === "available" ? "Available" : "Planned"}
                </span>
              </article>
            ))}
          </div>

          <p className="hint" style={{ marginTop: "2rem" }}>
            Looking for story printables? Visit the{" "}
            <Link href="/printables">Printables hub</Link>. For source-led study,
            start in <Link href="/knowledge">Knowledge</Link>.
          </p>
        </div>
      </section>
    </>
  );
}
